# 饶秋公众号文章 · 设计系统

## 品牌色：墨蓝（Ink Blue）

- 主色：`#15263D → #243A56`（渐变两端）
- 在代码里：`build_apple_style_publish.py` 顶部的 `INK_BLUE_DARK` / `INK_BLUE_LIGHT` 常量
- 来源："中国传统墨色干在纸上的蓝调，写字人的颜色"——对应饶秋"动笔思考 + AI 方法"的 IP 定位
- 用法：
  - 封面装饰短线（`INK_BLUE_LIGHT #243A56`）
  - 封面 radial gradient 光晕（不用主色，用更柔和的暖米 + 浅蓝）
  - 正文 eyebrow / blockquote 左边框（`#243A56`）
- **不再**用墨蓝做封面色块底（v8/v9 已废弃）

## 完整色板（在 `build_apple_style_publish.py` 顶部 `C` dict）

| 用途 | 色号 | 备注 |
|---|---|---|
| `ink`（正文主色） | `#1D1D1F` | 黑 |
| `sub`（次级文字） | `#6E6E73` | 中灰 |
| `muted`（边角小字） | `#86868B` | 浅灰 |
| `line`（分割线） | `#D2D2D7` | 极浅灰 |
| `bg`（页面底色） | `#FBFBFD` | 纸白 |
| `card`（代码底） | `#F5F5F7` | 浅卡片色 |
| **`accent`** | **`#243A56`** | **墨蓝** — eyebrow / blockquote / 装饰短线 |
| `accent_dark` | `#15263D` | 墨蓝 dark 端，备用 |

## 字体栈

**正文**（`FONT_STACK`）：
```
-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display',
'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', Arial, sans-serif
```

**标题**（`FONT_STACK_HEADING`）：
```
'Songti SC', 'Source Han Serif SC', 'Noto Serif CJK SC',
'Noto Serif SC', 'STSong', Georgia,
'PingFang SC', 'Microsoft YaHei', serif
```

**设计意图**：serif × sans 字体对比是高端编辑物的标准做法。中文 serif（宋体）标题 + sans（PingFang）正文，立刻把"博客感"切到"刊物感"。灵感来自 [nexu-io/html-anything](https://github.com/nexu-io/html-anything) 的 `doc-kami-parchment` skill。

## 字号体系

| 元素 | 字号 | weight | line-height | 字体 | 备注 |
|---|---|---|---|---|---|
| 顶部 h1 标题 | 26px | 700 | 1.35 | **serif** | letter-spacing 1px |
| 顶部 digest | 14.5px | 400 | 1.8 | sans | sub 色 |
| eyebrow（栏目铭牌） | 11.5px | 600 | — | sans | 墨蓝色，letter-spacing 3px，uppercase |
| 装饰短线（顶部） | 28×2px | — | — | — | 墨蓝色 |
| 正文 p | **15.5px** | 400 | **1.9** | sans | 主体阅读字号 |
| **h2** 二级标题 | **20px** | 600 | 1.4 | **serif** | margin 38↑ 12↓ |
| **h3** 三级标题 | **17px** | 600 | 1.45 | **serif** | margin 24↑ 8↓ |
| **h4** | 15.5px | 600 | 1.5 | **serif** | margin 18↑ 6↓ |
| ul / ol 列表 | 15.5px | 400 | 1.85 | sans | item margin 8px |
| blockquote | 15.5px | 400 | 1.9 | sans | 墨蓝左边框 3px |
| table 表头 th | 13.5px | 600 | — | sans | card 底色 |
| table 单元格 td | 14px | 400 | 1.7 | sans | |
| pre 代码块 | 13px | — | 1.7 | monospace | card 底色，border-radius 6px |
| inline code | 13px | — | — | monospace | card 底色，border-radius 3px |
| **分割线 `---`** | — | — | — | **serif** | 居中三点 `·  ·  ·`，14px muted，letter-spacing 14px |
| 关于饶秋 第一行 | 15px | 500 | 1.75 | sans | ink 色 |
| 关于饶秋 后两行 | 14px | 400 | 1.8 | sans | sub 色 |
| 关于饶秋 标识小字 | 11.5px | 600 | — | sans | muted 色 |

**设计逻辑**：
- **小字号 + 大行距** —— 从"博客感"切到"刊物感"
- **serif × sans 字体对比** —— 标题 serif、正文 sans，是高端编辑物的标准
- **分割线用三点不用横线** —— 出版物分章节的标配（The New Yorker / 单读 / 读库 都这么做）

## 容器 padding

```css
max-width: 677px;
margin: 0 auto;
padding: 28px 16px;
background: #FBFBFD;
```

**为什么 16px 水平 padding**：手机微信阅读容器自身有 ~16px 外边距，section 再加 16 ≈ 32px 总边距。是桌面预览 OK + 手机微信 OK 之间的最优解。

**历史路径**：`12px 4px`（太贴边）→ `32px 28px`（手机太窄）→ **`28px 16px`**（最终值）

## Preview HTML 设计原则

```html
<body style="margin:0;padding:24px 0;background:#FBFBFD;">
```

**preview body bg = section bg**，消除"灰底白卡"的双层框感。否则桌面浏览器预览会让人误判正文 padding 太多。

## 封面：Keynote 双行节奏（v10-D）

```
┌────────────────────────────────────────────────┐
│  AI 工 作 心 得                          N°06   │
│                                                │
│   我已经很少做 PPT 了 ──                        │  ← cover_kicker (22px sub gray)
│   HTML 被严重低估                               │  ← cover_title (auto-fit 44–60px)
│   ━━                                            │  ← 墨蓝装饰短线 36×3
│                                                │
└────────────────────────────────────────────────┘
   纸白底 #FBFBFD + 右上 #F4ECDD 暖米光 + 左下 #E2E8F0 浅蓝光
```

- 顶部 padding 50px：栏目标 14px sub gray + N°XX 14px sub gray
- 中部纵向居中：kicker + title + 墨蓝短线
- **没有 footnote / metadata stack** —— 所有元素 ≥ 14px，手机缩略图也读得清
- 标题字号自适应：60 → 58 → 56 → ... → 44 找最大能 1 行装下的字号

## 视觉禁区（硬规则）

以下元素**一律不进入**公众号文章（封面 / 正文 / 所有自动渲染都遵守）。

### ❌ 禁用

- **drop-shadow / box-shadow** — 任何文本或元素阴影
- **filter: blur** — 任何模糊效果
- **border-radius ≥ 8px** — 圆角太大显卡通；所有圆角必须 ≤ 6px
- **gradient（正文里）** — 正文不允许任何渐变色块、渐变文字。**例外**：封面 keynote 微渐变光影
- **霓虹色 / 高饱和色** — 单一墨蓝 `#243A56` 是唯一允许的强调色
- **rgba() 半透明色** — 用纯色十六进制
- **emoji 装饰** — 不要在 h2/h3/列表/段落前用 emoji 当 bullet 或装饰
- **彩色色块 / 高亮 / icon 装饰** — 不做"博客模板感"装饰
- **多种字体多种色** — 整篇就两套字体（serif 标题 + sans 正文）+ 两种色（ink + 墨蓝）+ 灰阶

### ✅ 允许且鼓励

- 1px hairline 描边
- 纯色单一强调（墨蓝 `#243A56`）
- 大量留白（小字号 + 大行距 1.85–1.9）
- **serif × sans 字体对比**
- 节奏感分割（`---` 渲染成居中 `·  ·  ·` 而不是横线）

**Why**：饶秋的 IP 是"安静的深度 + 讲真话 + 知行合一"。任何让封面/正文显得"AI 博主炸裂感"的视觉元素都直接伤害定位。这是硬规则，不是审美偏好——下次写新文章 / 加新功能时，先对照这个清单。

参考：[nexu-io/html-anything](https://github.com/nexu-io/html-anything) 的 `doc-kami-parchment` skill 的 "forbidden" 列表。
