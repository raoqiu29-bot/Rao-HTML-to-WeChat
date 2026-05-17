# 常见错误及修复

## 1. `invalid ip not in whitelist`

**症状**：`create_draft` 失败，错误信息显示 IP 不在白名单。

**原因**：当前出口 IP 没在公众号后台 IP 白名单。

**修复**：

```bash
# 查看当前出口 IP
curl -s https://api.ipify.org && echo

# 然后到 微信公众平台 → 设置与开发 → 基本配置 → IP白名单 添加该 IP
```

## 2. `No usable Python with Pillow found`

**症状**：`publish_apple_style.sh` 报找不到 Python with Pillow。

**修复**：

```bash
# 系统 python3 装 Pillow
python3 -m pip install Pillow

# 或者用 Codex 自带 runtime（已含 Pillow）
PYTHON=~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 ./publish_apple_style.sh "你的文章.md"
```

## 3. `md2wechat: command not found`

**症状**：脚本报 md2wechat 找不到。

**修复**：

```bash
export PATH="$HOME/.local/bin:$PATH"
md2wechat version --json
```

如果还是没有，需要先安装 md2wechat CLI：https://github.com/leetcode-mafia/md2wechat

## 4. 标题孤儿字（"了"单独一行）

**症状**：封面主标题最后一个字单独出现在第二行。

**原因**：标题字号自适应已经从 60 → 58 → ... → 44 找最大能 1 行装下的字号。如果标题太长仍 wrap 成 2 行且末尾孤儿字。

**修复**：
- 改 `cover_title` 用更短的关键词
- 或拆出关键词单独做 `cover_title`（参考 `cover-vs-title.md` 的模式 B）
- 例：`cover_title: "我用 HTML 替代了 PPT 这件事"` → 改成 `cover_title: "HTML 被严重低估"`

## 5. 封面文字 = 标题（重复）

**症状**：公众号文章列表里，封面上的大字和文章标题一样。

**原因**：没设 `cover_title`，自动 fallback 到 `title`。

**修复**：必须显式设 `cover_title`，且与 `title` 不同。详见 `cover-vs-title.md` 的 3 种模式 + 决策树。

## 6. 表格被渲染成普通段落

**症状**：md 里写的 `| 表头 | ... |` 没渲染成 `<table>`，变成纯文字。

**原因**：表格语法被破坏。

**修复**：
- 检查 `.wechat.html` 是否有 `<table` 标签
- 检查分隔行：`|---|---|---|`（不要有多余空格、对齐符号等异常）
- 表头行和分隔行之间不要有空行

回归测试：
```bash
grep -c "<table" *.wechat.html
# 应该返回 ≥ 1
```

## 7. 全角标点混在中文里有半角

**症状**：公众号读者看到 `,:;()` 半角标点混在中文里。

**原因**：源 markdown 没用全角标点。

**修复**：肉眼扫一遍源 md。半角 → 全角对照表见 `SKILL.md` 的"写作规范"段。

## 8. preview HTML 看着像"卡中卡"

**症状**：浏览器打开 `.preview.html` 看，灰底中间一块白卡感觉别扭。

**原因**：旧版 preview body bg 是灰色 `#EEF0F4`，section bg 是 `#FBFBFD`，造成双层框感。

**修复**：当前版本已修，preview body bg = section bg = `#FBFBFD`。如果你的预览仍是灰底，说明用了旧版脚本，重新构建即可。

## 9. 封面 radial gradient 不显示

**症状**：封面看不到右上暖光 + 左下蓝光的微渐变效果。

**原因**：可能是 Pillow 版本太旧不支持 BILINEAR 缩放，或者放大算法降级了。

**修复**：升级 Pillow 到最新版：
```bash
python3 -m pip install --upgrade Pillow
```

## 10. h2 标题没显示 serif 宋体

**症状**：浏览器或微信里 h2 标题看起来还是 sans-serif（PingFang）。

**原因**：
- 用户系统没装 Songti SC（极少见，macOS 自带）
- 字体 fallback 到了 `'PingFang SC'`（这是 fallback 链的最后一档）

**修复**：检查 `.wechat.html` 里 h2 的 `font-family` 是否包含 `'Songti SC'`。如果包含但仍是 sans 显示，说明 reader 端字体环境问题，无法在源头修复。

## 11. 草稿创建成功但封面不对

**症状**：`create_draft` 返回 success，但到公众号后台看封面不对。

**原因**：
- 上传封面前用的是旧版 `.cover.jpg`（脚本没重新生成）
- 或者 publish 流程中断后旧 `.draft.json` 残留

**修复**：删除中间产物，重跑：
```bash
rm 你的文章.{wechat.html,preview.html,cover.jpg,draft.json}
./publish_apple_style.sh "你的文章.md"
```
