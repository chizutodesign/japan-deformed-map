# -*- coding: utf-8 -*-
"""README用プレビュー画像を生成する（要 cairosvg）。
地方区分で塗り分けた例として dist/japan-rounded.svg を着色しPNG化。

usage: python3 build/preview.py
"""
import re, os
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

REGION = [
    (range(1, 2),   "#7FB5D5"),  # 北海道
    (range(2, 8),   "#8CC9B8"),  # 東北
    (range(8, 15),  "#F5B090"),  # 関東
    (range(15, 24), "#F2CE7E"),  # 中部
    (range(24, 31), "#E39898"),  # 近畿
    (range(31, 36), "#B8A8D6"),  # 中国
    (range(36, 40), "#93C29B"),  # 四国
    (range(40, 48), "#EDA0B7"),  # 九州・沖縄
]

def color(code):
    n = int(code)
    for rng, col in REGION:
        if n in rng:
            return col

with open(os.path.join(ROOT, "dist", "japan-rounded.svg"), encoding="utf-8") as f:
    svg = f.read()
svg = re.sub(r'(<path id="JP-(\d+)")',
             lambda m: f'{m.group(1)} fill="{color(m.group(2))}"', svg)
svg = svg.replace('</title>',
                  '</title>\n\t<rect x="-5" y="-5" width="290" height="260" fill="#FFFFFF"/>', 1)

out = os.path.join(ROOT, "assets", "preview.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out, output_width=1160)
print("OK:", out)
