# Frontmatter 字段完整参考

## 必需字段

| 字段 | 用途 | 微信限制 | 示例 |
|---|---|---|---|
| `title` | 微信文章标题（公众号列表/搜索/草稿标题） | ≤ 32 字 | `"AI 输出格式 · 我已经很少做 PPT 了"` |
| `author` | 微信文章作者 | ≤ 16 字 | `"饶秋"` |
| `digest` | 微信摘要 + 文章顶部 lede（不在封面显示） | ≤ 128 字 | 完整段落 |
| `eyebrow` | 左上角栏目铭牌 | — | `"AI 工作心得"` |
| `date` | 用于派生 year（备用）+ 微信归档 | YYYY-MM-DD | `"2026-05-06"` |

## 强烈建议字段（避免封面 = 标题翻车）

| 字段 | 用途 | 不设的后果 |
|---|---|---|
| `cover_title` | **封面图主标题**（大字） | fallback 到 `title`，但会与文章标题重复 |
| `cover_kicker` | 封面图引语（22px 小字） | fallback 到 `kicker`；都没有就只剩主标题，封面会显得空 |

**硬规则**：`cover_title` ≠ `title`。详见 `cover-vs-title.md` 的 3 种模式 + 决策树。

## 可选字段

| 字段 | 用途 | 默认 |
|---|---|---|
| `issue` | 封面右上角期号 | 从文件名前缀两位数字派生（如 `06-xxx.md` → `06`） |
| `topic` | 文章主题词（目前不在封面显示，保留扩展） | 空 |
| `category` | 文章分类（目前不在封面显示，保留扩展） | 空 |
| `type` | 文章类型标记（不影响渲染） | — |

## 完整示例

```yaml
---
title: "AI 输出格式 · 我已经很少做 PPT 了"
cover_title: "HTML 被严重低估"
cover_kicker: "我已经很少做 PPT 了 ——"
author: "饶秋"
digest: "AI 时代有一个被严重低估的格式叫 HTML。我和 AI 协作下来摸出一条线：对内的事用 Markdown，对外的事用 HTML。一个让 AI 给你能维护的内容，另一个让 AI 给你能直接发出去的成品。"
eyebrow: "AI 工作心得"
topic: "HTML"
category: "METHOD"
type: "wechat-article"
date: "2026-05-06"
---

## 你大概不知道，AI 还能直接给你做 PPT

正文从这里开始...
```

## YAML 写法注意事项

- 标题里有 `*` 或 `#` 字面符号（markdown 元字符）→ 必须用双引号包住：`title: "用 * 和 # 整理结构"`
- 中文标点用全角 `，：；（）""？！`（包括 frontmatter 里）
- `digest` 一般会比较长，直接写一段就行，YAML 会自动处理
- `date` 用 `YYYY-MM-DD` 格式（不要加 quotes 也行，但加 quotes 更安全）

## 字段查找逻辑（代码层）

`build_apple_style_publish.py` 的 `main()`：

```python
cover_title_text = meta.get("cover_title", title)           # cover_title 不设则用 title
cover_kicker_text = meta.get("cover_kicker", 
                              meta.get("kicker", ""))         # cover_kicker → kicker → 空

issue = meta.get("issue", "")
if not issue:
    m = re.match(r"^(\d{2,3})", SOURCE.stem)                 # 从文件名前缀派生
    if m:
        issue = m.group(1)

year = ""
date_str = meta.get("date", "")
if len(date_str) >= 4 and date_str[:4].isdigit():
    year = date_str[:4]
```

## 微信草稿 JSON 字段对应

```python
draft = {
    "articles": [{
        "title": meta["title"],                               # 微信文章标题
        "author": meta.get("author", "饶秋"),
        "digest": meta.get("digest", ""),
        "content": <封面 + 正文 HTML>,
        "thumb_media_id": <上传封面后返回的 media_id>,
        "show_cover_pic": 1,
    }]
}
```

注意：微信草稿的 `title` 字段对应 frontmatter 的 `title`，**不是** `cover_title`。`cover_title` 只用于封面图上的渲染。
