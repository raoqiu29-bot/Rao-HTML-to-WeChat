#!/usr/bin/env bash
# One-shot WeChat draft publisher for Apple-style articles.
#
# Usage:
#   ./publish_apple_style.sh 你的文章.md
#
# Or:
#   WECHAT_MD="你的文章.md" ./publish_apple_style.sh
#
# The script derives sibling asset paths from the markdown filename.

set -euo pipefail
cd "$(dirname "$0")"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 127
  fi
}

python_has_pillow() {
  "$1" - <<'PY' >/dev/null 2>&1
from PIL import Image, ImageDraw, ImageFont
PY
}

find_python() {
  if [[ -n "${PYTHON:-}" ]] && python_has_pillow "$PYTHON"; then
    printf '%s\n' "$PYTHON"
    return
  fi
  local candidates=(
    "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    "python3"
    "/usr/bin/python3"
  )
  local candidate resolved
  for candidate in "${candidates[@]}"; do
    if [[ "$candidate" == */* ]]; then
      [[ -x "$candidate" ]] || continue
      resolved="$candidate"
    else
      resolved="$(command -v "$candidate" 2>/dev/null || true)"
      [[ -n "$resolved" ]] || continue
    fi
    if python_has_pillow "$resolved"; then
      printf '%s\n' "$resolved"
      return
    fi
  done
  cat >&2 <<'EOF'
No usable Python with Pillow found.
Fix command:
  python3 -m pip install Pillow
Or run with a known Python:
  PYTHON=/path/to/python3 ./publish_apple_style.sh
EOF
  exit 1
}

require_cmd md2wechat
require_cmd jq

PY="$(find_python)"

MD="${1:-${WECHAT_MD:-}}"
if [[ -z "$MD" ]]; then
  printf 'Usage: %s <article.md>\n' "$0" >&2
  exit 2
fi
if [[ ! -f "$MD" ]]; then
  printf 'Article not found: %s\n' "$MD" >&2
  exit 2
fi

BASE="${MD%.md}"
HTML="${BASE}.wechat.html"
PREVIEW="${BASE}.preview.html"
COVER="${BASE}.cover.jpg"
DRAFT_JSON="${BASE}.draft.json"

echo "→ Pre-flight: 检查 digest 长度（微信 description 上限约 120 字，inspect 的 128 偏松会放行发不出去的稿）"
WECHAT_MD="$MD" "$PY" - <<'PYEOF'
import os, sys
text = open(os.environ["WECHAT_MD"], encoding="utf-8").read()
digest = ""
if text.startswith("---\n"):
    end = text.find("\n---\n", 4)
    if end != -1:
        for line in text[4:end].splitlines():
            if line.startswith("digest:"):
                v = line.split(":", 1)[1].strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                digest = v
                break
n = len(digest)
LIMIT = 118
if n > LIMIT:
    sys.stderr.write(f"\n[X] digest {n} 字 > 安全上限 {LIMIT} 字，微信会拒（errcode 45004 description out of limit）。\n")
    sys.stderr.write(f"    请把 frontmatter 的 digest 精简到 {LIMIT} 字以内再发。\n")
    sys.stderr.write(f"    当前 digest（{n} 字）: {digest}\n\n")
    sys.exit(3)
print(f"    digest {n} 字, OK（安全上限 {LIMIT}）")
PYEOF

echo "→ Building Apple-style assets from: $MD"
WECHAT_MD="$MD" WECHAT_HTML="$HTML" WECHAT_COVER="$COVER" WECHAT_PREVIEW="$PREVIEW" \
  "$PY" build_apple_style_publish.py >/dev/null

echo "→ Checking draft readiness"
md2wechat inspect "$MD" --cover "$COVER" --draft --json \
  | jq -e '.success == true and .data.readiness.draft_ready == true' >/dev/null

echo "→ Uploading cover to WeChat material library"
set +e
upload_json="$(md2wechat upload_image "$COVER" --json 2>&1)"
upload_status=$?
set -e
if [[ "$upload_status" -ne 0 ]]; then
  printf 'Cover upload failed:\n%s\n' "$upload_json" >&2
  exit "$upload_status"
fi
thumb_media_id="$(printf '%s' "$upload_json" | jq -r '.data.media_id // empty')"
if [[ -z "$thumb_media_id" ]]; then
  printf 'Cover upload did not return media_id:\n%s\n' "$upload_json" >&2
  exit 1
fi

echo "→ Assembling draft JSON"
MD_PATH="$MD" HTML_PATH="$HTML" JSON_PATH="$DRAFT_JSON" THUMB_MEDIA_ID="$thumb_media_id" "$PY" - <<'PY'
import json, os
md_file = os.environ["MD_PATH"]
html_file = os.environ["HTML_PATH"]
json_file = os.environ["JSON_PATH"]
text = open(md_file, encoding="utf-8").read()
meta = {}
if text.startswith("---\n"):
    end = text.find("\n---\n", 4)
    if end != -1:
        for line in text[4:end].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                v = v.strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                meta[k.strip()] = v
draft = {
    "articles": [{
        "title": meta["title"],
        "author": meta.get("author", "饶秋"),
        "digest": meta.get("digest", ""),
        "content": open(html_file, encoding="utf-8").read(),
        "thumb_media_id": os.environ["THUMB_MEDIA_ID"],
        "show_cover_pic": 1,
    }]
}
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(draft, f, ensure_ascii=False, indent=2)
PY

echo "→ Creating WeChat draft"
set +e
draft_json="$(md2wechat create_draft "$DRAFT_JSON" --json 2>&1)"
draft_status=$?
set -e
printf '%s\n' "$draft_json"
exit "$draft_status"
