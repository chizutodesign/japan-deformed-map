# -*- coding: utf-8 -*-
"""data/japan.grid.json から SVG を生成する。

正データはグリッドJSONのみ。SVGは常にこのスクリプトで再生成する。

usage:
    python3 build/generate.py

出力:
    dist/japan.svg                県名入り・角丸（既定）
    dist/japan-flat.svg           県名入り・白い境界線のフラットなスタイル
    dist/japan-nolabel.svg        県名なし・角丸
    dist/japan-flat-nolabel.svg   県名なし・フラット

基本形は「角丸＋県名入り」。-flat と -nolabel は引き算の修飾語。
何も指定せず dist/japan.svg を取った人がそのまま使える見た目にしてある。
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CELL = 10        # 1セル = 10 SVG units
PAD = 5          # viewBox の外周パディング（線のクリップ防止）
FONT = ('"IPAGothic", "Hiragino Sans", "Hiragino Kaku Gothic ProN", '
        '"Noto Sans JP", "Yu Gothic", Meiryo, sans-serif')
FONT_SIZE = 7    # ラベルの文字サイズ（最小の県が 20 units 角なので 2文字が収まる）
HALO = 1.2       # 県名の縁取りの太さ。太いと「白い座布団」に見え、細いと濃い塗りで沈む


def load():
    with open(os.path.join(ROOT, "data", "japan.grid.json"), encoding="utf-8") as f:
        return json.load(f)


def cells_by_key(data):
    out = defaultdict(set)
    for r, row in enumerate(data["rows"]):
        for c, ch in enumerate(row):
            if ch != ".":
                out[ch].add((c, r))
    return out


def trace_outline(cells):
    """セル集合から外周の頂点列（セル座標・時計回り）を得る。"""
    # 境界エッジを「県の内側が進行方向の左」になる向きで集める
    edges = {}  # start point -> end point
    for (c, r) in cells:
        if (c, r - 1) not in cells:   # 上辺: 左向き
            edges[(c + 1, r)] = (c, r)
        if (c, r + 1) not in cells:   # 下辺: 右向き
            edges[(c, r + 1)] = (c + 1, r + 1)
        if (c - 1, r) not in cells:   # 左辺: 下向き
            edges[(c, r)] = (c, r + 1)
        if (c + 1, r) not in cells:   # 右辺: 上向き
            edges[(c + 1, r + 1)] = (c + 1, r)
    start = next(iter(edges))
    pts = [start]
    p = edges[start]
    while p != start:
        pts.append(p)
        p = edges[p]
    assert len(pts) == len(edges), "外周が複数ループに分かれています"
    # 共線点をまとめる
    out = []
    n = len(pts)
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) != 0:
            out.append(b)
    return out


def inset_polygon(pts, d):
    """直交多角形を内側に d だけオフセットする。"""
    n = len(pts)
    # 各辺の内向き法線を決める（辺の中点から法線方向に少し進んだ点が内部かで判定）
    def inside(px, py):
        c = False
        for k in range(n):
            x1, y1 = pts[k]
            x2, y2 = pts[(k - 1) % n]
            if ((y1 > py) != (y2 > py)) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
                c = not c
        return c

    shifted = []  # 辺ごとの (固定軸, 値)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if y1 == y2:  # 水平辺 -> y を動かす
            s = 1 if inside(mx, my + 0.25) else -1
            shifted.append(("y", y1 + s * d))
        else:         # 垂直辺 -> x を動かす
            s = 1 if inside(mx + 0.25, my) else -1
            shifted.append(("x", x1 + s * d))
    out = []
    for i in range(n):
        a = shifted[i - 1]
        b = shifted[i]
        assert a[0] != b[0]
        x = a[1] if a[0] == "x" else b[1]
        y = a[1] if a[0] == "y" else b[1]
        out.append((x, y))
    return out


def rounded_path(pts, r):
    """直交多角形の各頂点を半径 r の円弧に置き換えた path d を返す。"""
    n = len(pts)
    d = []
    for i in range(n):
        p0 = pts[i - 1]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        v1 = (p1[0] - p0[0], p1[1] - p0[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1 = abs(v1[0]) + abs(v1[1])
        l2 = abs(v2[0]) + abs(v2[1])
        u1 = (v1[0] / l1, v1[1] / l1)
        u2 = (v2[0] / l2, v2[1] / l2)
        a = (p1[0] - u1[0] * r, p1[1] - u1[1] * r)   # 手前で止める
        b = (p1[0] + u2[0] * r, p1[1] + u2[1] * r)   # 先から出る
        sweep = 1 if (u1[0] * u2[1] - u1[1] * u2[0]) > 0 else 0
        cmd = "M" if i == 0 else "L"
        d.append(f"{cmd}{g(a[0])},{g(a[1])}")
        d.append(f"A{g(r)},{g(r)} 0 0 {sweep} {g(b[0])},{g(b[1])}")
    d.append("Z")
    return " ".join(d)


def g(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def header(data, w, h):
    return (
        f'<?xml version="1.0" encoding="utf-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{-PAD} {-PAD} {w * CELL + PAD * 2} {h * CELL + PAD * 2}" '
        f'role="img" aria-labelledby="map-title">\n'
        f'\t<title id="map-title">{data["name"]}</title>\n'
        f'\t<!-- generated from data/japan.grid.json - do not edit by hand -->\n'
        f'\t<!-- 1 cell = {CELL} units / grid {w} x {h} -->\n'
    )


def short_name(name):
    """ラベル用の短い県名。末尾の都/府/県を落とす（北海道はそのまま）。"""
    return name if name == "北海道" else re.sub(r"[都府県]$", "", name)


def labels(data, bykey, color="#333333", halo="#FFFFFF"):
    """県名ラベル。全県が矩形なので外接矩形の中心が必ず県の内側に入る。

    白いハロー（縁取り）を別グループとして下に敷く。塗り分けで背景が濃くなっても
    県名が読めるようにするため。paint-order 属性は対応しない描画系があるので使わず、
    テキストを2枚重ねる方式にしている。ハローが不要なら #label-halo を消せばよい。
    """
    order = sorted(data["legend"].items(), key=lambda kv: kv[1]["code"])
    pos = []
    for ch, meta in order:
        xs = [c for c, _ in bykey[ch]]
        ys = [r for _, r in bykey[ch]]
        pos.append((g((min(xs) + max(xs) + 1) * CELL / 2),
                    g((min(ys) + max(ys) + 1) * CELL / 2),
                    short_name(meta["name"])))

    def group(gid, extra, texts=pos):
        out = [f'\t<g id="{gid}" font-family=\'{FONT}\' font-size="{FONT_SIZE}" '
               f'text-anchor="middle" {extra}>\n']
        for x, y, name in texts:
            out.append(f'\t\t<text x="{x}" y="{y}" dominant-baseline="central">{name}</text>\n')
        out.append("\t</g>\n")
        return "".join(out)

    return (group("label-halo", f'fill="{halo}" stroke="{halo}" stroke-width="{HALO}" '
                                f'stroke-linejoin="round"')
            + group("labels", f'fill="{color}"'))


def bracket(data, inset=0.0):
    """沖縄の引き出し線。角を半径 BR で丸めた path にする。"""
    BR = 3
    (x1, y1), (x2, y2), (x3, y3) = [(p[0] * CELL, p[1] * CELL)
                                    for p in data["annotations"]["okinawa_bracket"]["points"]]
    # 横線 (x1,y1)->(x2,y2) ののち縦線 (x2,y2)->(x3,y3)。角(x2,y2)を丸める
    sx = 1 if x2 > x1 else -1
    sy = 1 if y3 > y2 else -1
    sweep = 1 if (sx * sy) > 0 else 0
    d = (f"M{g(x1)},{g(y1)} L{g(x2 - sx * BR)},{g(y2)} "
         f"A{BR},{BR} 0 0 {sweep} {g(x2)},{g(y2 + sy * BR)} L{g(x3)},{g(y3)}")
    return (f'\t<path id="okinawa-bracket" fill="none" '
            f'stroke="#333333" stroke-width="0.5" stroke-linecap="round" d="{d}"/>\n')


def write(name, parts):
    with open(os.path.join(ROOT, "dist", name), "w", encoding="utf-8") as f:
        f.write("".join(parts))


def main():
    data = load()
    w, h = data["grid"]["cols"], data["grid"]["rows"]
    bykey = cells_by_key(data)
    order = sorted(data["legend"].items(), key=lambda kv: kv[1]["code"])

    # --- 1) フラット白地図 ---
    body = [header(data, w, h),
            '\t<g id="prefectures" fill="#E8E8E8" stroke="#FFFFFF" '
            'stroke-width="1" stroke-linejoin="round">\n']
    for ch, meta in order:
        pts = trace_outline(bykey[ch])
        p = " ".join(f"{x * CELL},{y * CELL}" for x, y in pts)
        body.append(f'\t\t<polygon id="JP-{meta["code"]}" data-name="{meta["name"]}" '
                    f'data-romaji="{meta["romaji"]}" points="{p}">'
                    f'<title>{meta["name"]}</title></polygon>\n')
    body.append("\t</g>\n")
    body.append(bracket(data))
    write("japan-flat-nolabel.svg", body + ["</svg>\n"])
    write("japan-flat.svg", body + [labels(data, bykey), "</svg>\n"])

    # --- 2) 角丸・隙間ありスタイル ---
    INSET, R = 1.0, 3.0
    body = [header(data, w, h), '\t<g id="prefectures" fill="#F5B090">\n']
    for ch, meta in order:
        pts = trace_outline(bykey[ch])
        pts = [(x * CELL, y * CELL) for x, y in pts]
        d = rounded_path(inset_polygon(pts, INSET), R)
        body.append(f'\t\t<path id="JP-{meta["code"]}" data-name="{meta["name"]}" '
                    f'data-romaji="{meta["romaji"]}" d="{d}">'
                    f'<title>{meta["name"]}</title></path>\n')
    body.append("\t</g>\n")
    body.append(bracket(data, inset=INSET))
    write("japan-nolabel.svg", body + ["</svg>\n"])
    write("japan.svg", body + [labels(data, bykey), "</svg>\n"])

    print(f"OK: dist/japan.svg, dist/japan-flat.svg, "
          f"dist/japan-nolabel.svg, dist/japan-flat-nolabel.svg "
          f"({len(order)} prefectures)")


if __name__ == "__main__":
    main()
