# -*- coding: utf-8 -*-
"""生成されたSVGが正データ（data/japan.grid.json）と一致するか検証する。

usage: python3 build/verify.py
すべてOKなら exit 0、不一致があれば exit 1。
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CELL = 10


def inside(px, py, pts):
    c = False
    n = len(pts)
    for k in range(n):
        x1, y1 = pts[k]
        x2, y2 = pts[(k - 1) % n]
        if ((y1 > py) != (y2 > py)) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
            c = not c
    return c


def main():
    with open(os.path.join(ROOT, "data", "japan.grid.json"), encoding="utf-8") as f:
        data = json.load(f)
    W, H = data["grid"]["cols"], data["grid"]["rows"]

    truth = {}
    for r, row in enumerate(data["rows"]):
        for c, ch in enumerate(row):
            if ch != ".":
                truth[(c, r)] = data["legend"][ch]["code"]

    codes = sorted(v["code"] for v in data["legend"].values())
    ok = True
    if codes != [f"{i:02d}" for i in range(1, 48)]:
        print("NG: legend のコードが 01-47 と一致しません")
        ok = False

    with open(os.path.join(ROOT, "dist", "japan-flat-nolabel.svg"), encoding="utf-8") as f:
        svg = f.read()

    got = {}
    for m in re.finditer(r'id="JP-(\d+)"[^>]*points="([^"]+)"', svg):
        code = m.group(1)
        n = [float(x) for x in re.findall(r"-?\d+\.?\d*", m.group(2))]
        pts = [(n[k] / CELL, n[k + 1] / CELL) for k in range(0, len(n), 2)]
        for x in n:
            if x != int(x):
                print(f"NG: JP-{code} に非整数座標 {x}")
                ok = False
        for r in range(H):
            for c in range(W):
                if inside(c + 0.5, r + 0.5, pts):
                    got[(c, r)] = code

    # ラベル版に47県すべての名前が入っているか
    for fn in ("japan.svg", "japan-flat.svg"):
        path = os.path.join(ROOT, "dist", fn)
        if not os.path.exists(path):
            print(f"NG: dist/{fn} がありません")
            ok = False
            continue
        with open(path, encoding="utf-8") as f:
            texts = re.findall(r"<text[^>]*>([^<]+)</text>", f.read())
        want = sorted(v["name"] if v["name"] == "北海道"
                      else re.sub(r"[都府県]$", "", v["name"])
                      for v in data["legend"].values())
        if sorted(texts) != want:
            print(f"NG: dist/{fn} のラベルが正データと不一致（{len(texts)}件）")
            ok = False

    if got != truth:
        diff = {k for k in set(truth) | set(got) if truth.get(k) != got.get(k)}
        print(f"NG: セル占有が正データと不一致（{len(diff)}セル）: {sorted(diff)[:10]}")
        ok = False
    else:
        print(f"OK: 47都道府県 / {len(truth)}セル一致 / 全座標整数")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
