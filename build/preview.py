# -*- coding: utf-8 -*-
"""README用プレビュー画像を生成する（要 cairosvg）。
地方区分で塗り分けた例として svg/japan.svg を着色しPNG化。

usage: python3 build/preview.py
"""
import re, os, subprocess
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# cairosvg は font-family のリストを解決できず、実在する単一のファミリー名しか扱えない
# （リストを渡すと豆腐になる）。そのため実行環境にあるものを1つ選んで差し替える。
# svg/ のSVG自体は書き換えないので、配布物のフォント指定には影響しない。
FONT_CANDIDATES = ["Hiragino Sans", "Yu Gothic", "Noto Sans CJK JP", "Noto Sans JP", "IPAGothic"]


def pick_font():
    try:
        installed = subprocess.run(["fc-list", "--format", "%{family}\n"],
                                   capture_output=True, text=True, check=True).stdout.lower()
    except (OSError, subprocess.CalledProcessError):
        return FONT_CANDIDATES[0]
    for fam in FONT_CANDIDATES:
        if fam.lower() in installed:
            return fam
    raise SystemExit("NG: 日本語フォントが見つかりません。" + " / ".join(FONT_CANDIDATES) + " のいずれかを入れてください")


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

with open(os.path.join(ROOT, "svg", "japan.svg"), encoding="utf-8") as f:
    svg = f.read()
svg = re.sub(r'(<path id="JP-(\d+)")',
             lambda m: f'{m.group(1)} fill="{color(m.group(2))}"', svg)
font = pick_font()
svg = re.sub(r"font-family='[^']*'", f"font-family='{font}'", svg)

svg = svg.replace('</title>',
                  '</title>\n\t<rect x="-5" y="-5" width="290" height="260" fill="#FFFFFF"/>', 1)

out = os.path.join(ROOT, "assets", "preview.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out, output_width=1160)
print(f"OK: {out}  (font: {font})")
