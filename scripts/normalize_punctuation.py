#!/usr/bin/env python3
"""把 Markdown 正文里挨着中文的半角标点转成全角(发公众号前规范化)。
保护:代码块 ```...```、inline code `...`、命令/英文语境的半角标点。
用法: python3 normalize_punctuation.py <文章.md>
"""
import re, sys

if len(sys.argv) < 2:
    print("用法: python3 normalize_punctuation.py <文章.md>"); sys.exit(1)

path = sys.argv[1]
s = open(path, encoding="utf-8").read()

# 中文字 + 中文标点(顿号、书名号、全角符号、弯引号、省略号、破折号等)
CJK = r'[一-鿿　-〿＀-￯‘-‟…—]'
PAIRS = {',': '，', ':': '：', ';': '；', '?': '？', '!': '！'}

def conv(t):
    for h, f in PAIRS.items():
        t = re.sub(rf'(?<={CJK}){re.escape(h)}', f, t)   # 中文 + 半角
        t = re.sub(rf'{re.escape(h)}(?={CJK})', f, t)     # 半角 + 中文
    # 括号:任一侧贴中文即转
    t = re.sub(rf'(?<={CJK})\(', '（', t)
    t = re.sub(rf'\((?={CJK})', '（', t)
    t = re.sub(rf'(?<={CJK})\)', '）', t)
    t = re.sub(rf'\)(?={CJK})', '）', t)
    return t

out, in_code = [], False
for line in s.split('\n'):
    if line.strip().startswith('```'):
        in_code = not in_code; out.append(line); continue
    if in_code:
        out.append(line); continue
    # 行内 inline code 用 ` 包裹 → 偶数段是普通文本,奇数段是代码(跳过)
    parts = line.split('`')
    for i in range(0, len(parts), 2):
        parts[i] = conv(parts[i])
    out.append('`'.join(parts))

open(path, "w", encoding="utf-8").write('\n'.join(out))
print(f"✓ 全角规范化完成: {path}")
