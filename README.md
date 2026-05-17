# Rao HTML to WeChat

> 把 Markdown 文章一键转成饶秋老师锁定的 Apple Keynote 极简风微信公众号草稿。

**Apple Keynote 极简风 + 墨蓝 `#243A56` 品牌色 + serif × sans 字体对比 + 排版精算 + 自动上传封面 + 创建草稿到公众号草稿箱。**

[![Skill](https://img.shields.io/badge/Claude%20Skill-raoqiu--html--to--wechat-1abc9c?style=flat-square)](#installation)
[![Version](https://img.shields.io/badge/version-v1.0.0-blue?style=flat-square)](#)
[![License](https://img.shields.io/badge/license-MIT-orange?style=flat-square)](LICENSE)
[![Brand Color](https://img.shields.io/badge/brand-墨蓝%20%23243A56-243A56?style=flat-square)](#design-system)

## ✨ 这是什么

一个 Claude Code skill，把任意 Markdown 文章一键转成微信公众号草稿。所有设计决策都已锁定，跑就完事：

- ✅ **微信兼容内联 HTML**（不依赖 `<style>` 标签、外链 CSS）
- ✅ **Keynote 双行节奏封面**（kicker + 主标题 + 墨蓝装饰短线 + 微渐变光影）
- ✅ **serif × sans 字体对比**（Songti SC 标题 + PingFang sans 正文，刊物级排版）
- ✅ **墨蓝 `#243A56` 单色 accent**（封面 + 正文统一品牌色）
- ✅ **一键上传封面 + 创建草稿**（用 [`md2wechat`](https://github.com/leetcode-mafia/md2wechat) 走微信草稿接口）
- ✅ **9 条视觉禁区硬规则**（no shadow / no blur / no gradient in body / no neon / ...）

## 📦 安装

### 前置依赖

```bash
# md2wechat CLI
brew install md2wechat   # 或参考 md2wechat 官方安装指南

# Pillow（封面图生成）
python3 -m pip install Pillow

# jq（JSON 处理）
brew install jq
```

### 配置微信公众号

把 AppID / AppSecret 写到 `~/.config/md2wechat/config.yaml`，并把当前出口 IP 加到公众号后台 IP 白名单。

### 安装 skill 到 Claude Code

```bash
git clone https://github.com/raoqiu29-bot/Rao-HTML-to-WeChat.git ~/.claude/skills/raoqiu-html-to-wechat
```

或者用 symlink（推荐，方便本地开发）：

```bash
git clone https://github.com/raoqiu29-bot/Rao-HTML-to-WeChat.git ~/your/path/raoqiu-html-to-wechat
ln -s ~/your/path/raoqiu-html-to-wechat ~/.claude/skills/raoqiu-html-to-wechat
```

重启 Claude Code，输入 `/raoqiu-html-to-wechat` 即可调用。

## 🚀 用法

### 1. 写 Markdown 文章，frontmatter 必须包含：

```yaml
---
title: "AI 输出格式 · 我已经很少做 PPT 了"   # 微信文章标题
cover_title: "HTML 被严重低估"              # 封面主标题（必须 ≠ title）
cover_kicker: "我已经很少做 PPT 了 ——"      # 封面引语
author: "饶秋"
digest: "AI 时代有一个被严重低估的格式叫 HTML..."   # 微信摘要（≤ 128 字）
eyebrow: "AI 工作心得"                       # 左上角栏目铭牌
date: "2026-05-06"
issue: "06"                                  # 可选：封面右上期号
---

## 正文从这里开始...
```

### 2. 一键发布到微信草稿箱

```bash
./scripts/publish_apple_style.sh "你的文章.md"
```

完成后返回 `media_id`，到公众号后台 → 草稿箱 → 预览 / 发表。

### 3. 只生成预览（不上传微信）

```bash
WECHAT_MD="你的文章.md" \
WECHAT_HTML="你的文章.wechat.html" \
WECHAT_PREVIEW="你的文章.preview.html" \
WECHAT_COVER="你的文章.cover.jpg" \
python3 scripts/build_apple_style_publish.py
open "你的文章.preview.html"
```

## 🎨 设计系统（Design System）

### 品牌色：墨蓝（Ink Blue）

`#15263D → #243A56` —— 中国传统墨色干在纸上的蓝调，"写字人的颜色"。

### 封面布局：Keynote 双行节奏

```
┌────────────────────────────────────────────────┐
│  AI 工 作 心 得                          N°06   │
│                                                │
│   我已经很少做 PPT 了 ──                        │  ← cover_kicker (22px)
│   HTML 被严重低估                               │  ← cover_title (44-60px)
│   ━━                                            │  ← 墨蓝装饰短线
│                                                │
└────────────────────────────────────────────────┘
   纸白底 #FBFBFD + 右上暖米光 + 左下浅蓝光（微渐变光影）
```

### 字体对比

- **标题**：Songti SC / Noto Serif SC（serif）
- **正文**：PingFang SC / -apple-system（sans）

### 字号体系（小字号 + 大行距 = 刊物感）

| 元素 | 字号 | line-height |
|---|---|---|
| h1 | 26px | 1.35 |
| h2 | 20px | 1.4 |
| h3 | 17px | 1.45 |
| p | 15.5px | 1.9 |

### 视觉禁区（硬规则）

❌ shadow · blur · gradient（正文）· rounded ≥ 8px · neon · rgba · emoji 装饰

✅ 1px hairline · 单色墨蓝 · 大量留白 · serif × sans 对比 · 三点分割 `·  ·  ·`

详见 [`references/design-system.md`](references/design-system.md)。

## 📐 封面 vs 文章标题：3 种模式

**硬规则**：`cover_title` 不能等于 `title`。

| 模式 | 适合 | 例 |
|---|---|---|
| **A · 故事 + 论点 split**（推荐默认） | 内容有"个人叙事 + 强论点"两个钩子 | title=故事 / cover_title=论点 |
| **B · 强论点 single** | 标题长或只有一个论点 | title=完整描述 / cover_title=短关键词 / cover_kicker=空 |
| **C · 完全分离** | 多个钩子角度 | title 和 cover_* 两组完全不同钩子 |

详见 [`references/cover-vs-title.md`](references/cover-vs-title.md)。

## 📁 文件结构

```
raoqiu-html-to-wechat/
├── SKILL.md                          ← Claude Code skill 主入口
├── README.md                         本文件
├── LICENSE                           MIT
├── scripts/
│   ├── build_apple_style_publish.py  Markdown → HTML + Cover 渲染器（Python + PIL）
│   └── publish_apple_style.sh        一键发布脚本（bash + md2wechat）
├── references/
│   ├── design-system.md              色板 / 字号 / 视觉禁区硬规则
│   ├── cover-vs-title.md             封面 vs 标题：3 种模式 + 决策树
│   ├── frontmatter-fields.md         字段表 + 示例
│   └── troubleshooting.md            常见错误及修复
└── examples/
    └── article-with-frontmatter.md   示例文章（含完整 frontmatter）
```

## 🧠 设计灵感

- [`tw93/kami`](https://github.com/tw93/kami) — warm parchment editorial style
- [`nexu-io/html-anything`](https://github.com/nexu-io/html-anything) — agentic HTML editor，`doc-kami-parchment` skill 的视觉禁区列表对得上饶秋"安静的深度"IP
- Apple Keynote 微渐变光影
- 麦肯锡 / HBR 编辑式排版

## 🙋 这个 skill 为谁而做？

为饶秋老师本人量身定制——所有视觉决策都对应到他的 IP 定位（"安静的深度 + 讲真话 + 知行合一"），不打算适用所有公众号作者。

如果你也想用类似的视觉语言，建议：
- ✅ Fork 这个 repo，替换 `build_apple_style_publish.py` 里的 `INK_BLUE_*` 颜色、`FONT_STACK_*`、`AUTHOR_BIO_HTML` 改成你自己的
- ✅ 在你自己的文章 frontmatter 里用同一套字段结构
- ⚠️ "墨蓝 + Songti SC + Keynote 双行节奏"是饶秋的视觉身份，不要原样复用，避免视觉冲突

## 🔗 相关 skill

- [`Rao-HTML-PPT-Builder`](https://github.com/raoqiu29-bot/Rao-HTML-PPT-Builder) — 麦肯锡风 HTML PPT 生成
- `raoqiu-html-to-xhs` — 小红书图文生成（私有）

## 📄 License

[MIT](LICENSE) © 饶秋（[@raoqiu29-bot](https://github.com/raoqiu29-bot)）
