---
name: raoqiu-html-to-wechat
zh_name: "饶秋老师 HTML 公众号文章生成器"
en_name: "Rao HTML to WeChat"
emoji: "📝"
description: 把 Markdown 文章一键转成饶秋老师锁定的 Apple Keynote 极简风微信公众号草稿——含墨蓝 #243A56 品牌色 + Keynote 双行节奏封面（kicker + 主标题 + 装饰短线 + 微渐变光影）+ serif × sans 字体对比 + 排版精算的正文 + 自动上传封面到微信素材库 + 创建草稿到公众号草稿箱。当用户要求"发公众号""做公众号文章""把这篇 md 推到微信草稿箱""按饶秋老师的公众号风格排版""生成公众号封面""更新公众号草稿"时，必须使用此技能。即使用户没明说"饶秋风格"，只要意图是把一段 Markdown 内容做成微信公众号文章 + 封面 + 草稿一条龙，都应触发。配套硬规则：封面文字 ≠ 文章标题（3 种模式 + 决策树）、视觉禁区（no shadow / no blur / no gradient in body / no neon / no rgba）、墨蓝单色 accent、serif 标题 + sans 正文。
category: article
scenario: wechat-publishing
surface: ["wechat-article", "wechat-draft", "html-share"]
design_system: apple-keynote-ink-blue
brand_color: "#243A56"
aspect_hint: "公众号 677px 阅读区 · 封面 900×383"
modes: ["one-shot-publish", "preview-only"]
version: "1.0.0"
tags: ["wechat", "公众号", "微信文章", "草稿", "封面", "排版", "raoqiu", "apple-keynote", "ink-blue", "墨蓝"]
repo: "https://github.com/raoqiu29-bot/Rao-HTML-to-WeChat"
license: MIT
---

# 饶秋老师 HTML 公众号文章生成技能

## 这是什么

把任意一篇 Markdown 文章（含 YAML frontmatter）一键转成饶秋老师锁定的微信公众号草稿：

- **微信兼容内联 HTML**（所有样式写在 `style` 属性里，符合 WeChat 草稿接口要求）
- **本地预览 HTML**（浏览器直接打开看排版）
- **公众号封面图 JPG**（900×383，Keynote 双行节奏 + 墨蓝装饰）
- **上传封面到微信素材库** + **创建草稿到公众号草稿箱**

整套工作流跑通后，用户到公众号后台点"发表"即可。

## 触发场景

只要满足以下任一条件，必须使用此技能：

1. 用户提到"发公众号""做公众号文章""推到微信草稿箱""生成公众号封面""更新公众号草稿"
2. 用户提到"按饶秋老师的公众号风格排版""按饶秋的 keynote 风做封面""墨蓝品牌色"
3. 用户上传一份 Markdown 文章，要求转成微信公众号草稿
4. 即使用户只说"把这篇推到微信"，只要内容是文章而非营销文档，都应触发

不该用此技能的情况：
- 用户要做 PPT / Keynote / 演示稿 → 用 `raoqiu-slide-builder`
- 用户要做小红书图文 → 用 `raoqiu-html-to-xhs`
- 用户要做营销活动方案 → 用 `marketing-doc-formatter`

## 设计语言概要（详细见 `references/design-system.md`）

**品牌色**：墨蓝 Ink Blue `#15263D → #243A56`
- 中国传统墨色干在纸上的蓝调，"写字人的颜色"
- 仅用作装饰短线 + eyebrow + blockquote 边框 + 封面光晕；正文文字仍用 ink `#1D1D1F`

**封面布局**：Keynote 双行节奏（v10-D）
- 纸白底 `#FBFBFD` + 双 radial gradient（右上暖米光 + 左下浅蓝光）
- 顶部：栏目标（左）+ N°XX 期号（右）
- 中部居中：`cover_kicker`（22px sub gray）+ `cover_title`（auto-fit 44–60px）+ 墨蓝装饰短线 36×3
- 没有 footnote / 没有 metadata stack，所有元素 ≥ 14px

**字体对比**：serif 标题 + sans 正文
- h1/h2/h3/h4 用 `FONT_STACK_HEADING`（Songti SC / Noto Serif SC 优先）
- 正文 / 列表 / 引用用 `FONT_STACK`（PingFang SC sans 优先）

**正文排版**：小字号 + 大行距
- p 15.5px / line-height 1.9
- h1 26px / h2 20px / h3 17px / h4 15.5px
- 容器 padding 28px 16px（手机 + 桌面双优）

**视觉禁区（硬规则）**：详见 `references/design-system.md`
- ❌ shadow / blur / gradient（正文里）/ rounded ≥ 8px / neon / rgba()
- ✅ 1px hairline / 单色墨蓝 / serif × sans 对比 / 三点分割 `·  ·  ·`

## 工作流：3 种模式

### Mode A · 一键全发布（最常用）

```bash
"$SKILL_PATH"/scripts/publish_apple_style.sh "你的文章.md"
```

完成：构建 HTML + 生成封面 + 上传封面到微信素材库 + 创建草稿。返回 `media_id`，用户到公众号后台草稿箱发表。

### Mode B · 只生成预览（不上传微信）

适合写作中反复调整时。

```bash
WECHAT_MD="你的文章.md" \
WECHAT_HTML="你的文章.wechat.html" \
WECHAT_PREVIEW="你的文章.preview.html" \
WECHAT_COVER="你的文章.cover.jpg" \
python3 "$SKILL_PATH"/scripts/build_apple_style_publish.py
open "你的文章.preview.html"
```

### Mode C · 发布前检查

```bash
md2wechat inspect "你的文章.md" --cover "你的文章.cover.jpg" --draft --json
```

重点看 `data.readiness.draft_ready` 是否为 `true`、标题 ≤ 32 字、作者 ≤ 16 字、摘要 ≤ 128 字。

## 必需的 frontmatter 字段（详细见 `references/frontmatter-fields.md`）

```yaml
---
title: "AI 输出格式 · 我已经很少做 PPT 了"   # 微信文章标题
cover_title: "HTML 被严重低估"              # 封面主标题（≠ title）
cover_kicker: "我已经很少做 PPT 了 ——"      # 封面引语
author: "饶秋"
digest: "AI 时代有一个被严重低估的格式叫 HTML..."   # 微信摘要（≤ 128 字）
eyebrow: "AI 工作心得"                       # 左上角栏目铭牌
date: "2026-05-06"
issue: "06"                                  # 可选：右上期号
topic: "HTML"                                # 可选
category: "METHOD"                           # 可选
---
```

**硬规则：`cover_title` ≠ `title`。** 重复 = 业余 = 阅读量低。详见 `references/cover-vs-title.md` 的 3 种模式 + 决策树。

## 写作规范（硬规则）

### 1. 中文正文必须用全角标点

| 半角（错） | 全角（对） |
|---|---|
| `,` | `，` |
| `:` | `：` |
| `;` | `；` |
| `(` `)` | `（` `）` |
| `"..."` | `"..."` |
| `?` | `？` |
| `!` | `！` |

例外：英文单词内、文件路径、代码块、inline code、Markdown 表格分隔符 `|---|` 保持原样。

### 2. GFM 表格已支持

直接在 md 里写 `| 表头 | ... |` + `|---|---|`，会渲染成带样式的 `<table>`。

### 3. 分割线用 `---`

会渲染成居中三点 `·  ·  ·`（serif，14px muted）—— 出版物分章节的标准做法。

### 4. GFM Alert 提示框（v1.1 新增）

参考 [`doocs/md`](https://github.com/doocs/md) 的实现，支持 5 种语义化提示框。在 markdown 里写：

```markdown
> [!NOTE]
> 这是一个 NOTE 注释。补充信息、背景说明。

> [!TIP]
> 这是一个 TIP 小贴士。实用建议、节省时间的做法。

> [!IMPORTANT]
> 这是一个 IMPORTANT 重点。核心结论、最关键的判断。

> [!WARNING]
> 这是一个 WARNING 注意。潜在风险、容易踩的坑。

> [!CAUTION]
> 这是一个 CAUTION 警示。严重后果、不可挽回的错误。
```

渲染：墨蓝左边框 + 墨蓝铭牌标签 + ink 正文。符合视觉禁区"no colored boxes"硬规则。

### 5. WeChat 草稿字符上限（v1.1 新增）

**微信公众号草稿 API 单篇硬限制：< 20,000 字符**（包括所有 inline style）。

`build_apple_style_publish.py` 会在构建时检查：
- HTML > 19,000 字符 → ⚠️ 警告（建议精简）
- HTML > 20,000 字符 → ❌ 错误（草稿创建会失败）

精简方法：
- 拆分长文成上下两篇
- 减少 inline `<style>` 占用（当前已经用最简语法）
- 删除非必要的装饰元素

## 已验证环境前置

- `md2wechat` CLI 已安装（PATH 应含 `~/.local/bin`）
- 微信 AppID/AppSecret 已写入 `~/.config/md2wechat/config.yaml`
- 当前出口 IP 在公众号后台 IP 白名单
- Pillow 已安装（系统 `python3 -m pip install Pillow` 或用 Codex 自带 runtime）

## 验收清单

发完 `publish_apple_style.sh` 之后做这几个检查：

1. **封面**：`open *.cover.jpg`——栏目标 + N°XX + kicker + 主标题 + 短线五件齐全；最大字 1 行无孤儿字；右上暖光 / 左下蓝光能感觉到但不抢戏
2. **正文**：`open *.preview.html`——左右不贴边、字号舒服、无双层框感
3. **表格**：如果 md 里有表格，`grep -c "<table" *.wechat.html` ≥ 1
4. **封面 ≠ 标题**：`cover_title` 必须与 `title`（含 prefix）不同
5. **全角标点**：肉眼扫一遍 `.wechat.html`，确认无半角 `,:;()` 混在中文里

## 常见错误（详见 `references/troubleshooting.md`）

- `invalid ip not in whitelist` → 把当前出口 IP 加到公众号 IP 白名单
- `No usable Python with Pillow found` → `python3 -m pip install Pillow`
- `md2wechat command not found` → `export PATH="$HOME/.local/bin:$PATH"`
- 标题孤儿字（"了"单独一行）→ 标题字号已经从 60 自适应到 44 找最大值，如仍 wrap 建议改 `cover_title` 用更短关键词
- 封面文字 = 标题 → 必须设 `cover_title`（≠ `title`）

## 文件结构

```
raoqiu-html-to-wechat/
├── SKILL.md                          ← 你正在读
├── README.md                         GitHub 介绍页
├── LICENSE                           MIT
├── scripts/
│   ├── build_apple_style_publish.py  Markdown → HTML + Cover 渲染器
│   └── publish_apple_style.sh        一键发布脚本
├── references/
│   ├── design-system.md              色板 / 字号 / 视觉禁区硬规则
│   ├── cover-vs-title.md             封面 vs 标题：3 种模式 + 决策树
│   ├── frontmatter-fields.md         字段表 + 示例
│   └── troubleshooting.md            常见错误及修复
└── examples/
    └── article-with-frontmatter.md   示例文章（含完整 frontmatter）
```

## 历史踩坑记录（避免下次重犯）

1. **半屏色块封面（v8/v9）已废弃**：手机缩略图小字读不清；左白 + 右色块的"双层框"显得不合理
2. **全角标点翻车**：源 markdown 用半角 `,:`，渲染到公众号读者眼前显得不专业
3. **表格被当成段落**：早期不支持 GFM 表格，`|---|---|` 字面值出现在正文里
4. **双层 padding 错觉**：preview HTML 灰底 + section 白卡造成"卡中卡"。改成 preview body bg = section bg
5. **封面 = 标题翻车**：必须用 `cover_title` 与 `title` 分离
6. **大字反而丑**：96px 大字在中文里显压迫；54–60px + 大留白才高级
7. **Apple 蓝 accent 与封面不统一**：正文 accent 已从 `#0071E3` 切到墨蓝 `#243A56`

## 仓库与版本

- GitHub：https://github.com/raoqiu29-bot/Rao-HTML-to-WeChat
- 当前版本：v1.0.0
- License：MIT
