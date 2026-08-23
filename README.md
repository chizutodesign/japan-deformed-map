# デフォルメ日本地図 / Deformed Map of Japan

<img src="assets/preview.png" width="480" alt="デフォルメ日本地図（地方区分で塗り分けた例）">

都道府県を単純な四角形の組み合わせに簡略化した日本地図です。全図形が **28×25の正方形グリッド** に乗っており、SVG・JSONの2形式で提供します。データ可視化やWebサイト、AIとの対話など、自由に使えます。

- **SVG** — 全座標が整数（1セル = 10単位）。各都道府県に `id="JP-13"`（ISO 3166-2:JP）付き
- **JSON** — 1セル1文字のテキストグリッド。プログラムからもLLMからもそのまま読めます

## ファイル

| ファイル | 内容 |
|---|---|
| `data/japan.grid.json` | 正データ（グリッド＋凡例）。編集するのはこのファイルだけ |
| `svg/japan.svg` | **県名入り・角丸。まずはこれ** |
| `svg/japan-flat.svg` | 県名入り・白い境界線のフラットなスタイル |
| `svg/japan-nolabel.svg` | 県名なし・角丸（自分でラベルや数値を載せる人向け） |
| `svg/japan-flat-nolabel.svg` | 県名なし・フラット |
| `build/generate.py` | JSON → SVG 生成スクリプト |
| `build/verify.py` | 生成されたSVGが正データと一致するかの検証スクリプト |
| `build/preview.py` | README用プレビュー画像の生成（要 cairosvg） |
| `examples/` | 使用例（CSS Grid描画・SVG塗り分け） |

## どちらを使うか

| やりたいこと | 使うファイル |
|---|---|
| そのまま見せる・値で塗り分ける | `svg/japan.svg` |
| 県名も自分で配置したい（数値を併記するなど） | `svg/japan-nolabel.svg` / `svg/japan-flat-nolabel.svg` |
| 都道府県コードでデータを結合する・AIに読ませる | `data/japan.grid.json` |

グリッドJSONのセルをそのまま描画すると、都道府県が分割されたタイル状の表現になります。それを意図している場合を除き、描画にはSVGを使ってください。

塗り分けるときも県名入りのファイルをそのまま使えます。県名には白い縁取り（`<g id="label-halo">`）を敷いてあるので、塗りが濃くても薄くてもそのまま読めます。文字色を調整する必要はありません。縁取りが不要なら、そのグループを消してください。

## 使い方

### ダウンロードして使う

[Releases](https://github.com/chizutodesign/japan-deformed-map/releases/latest) の **Source code (zip)** に一式が入っています。展開して `svg/japan.svg` を Illustrator・Figma・Inkscape などで開けば、そのまま編集できます。県名はテキストとして入っているので、文字のまま差し替えや書体変更ができます。

SVG1枚だけ欲しい場合は、次のURLを開いて保存してください。

https://cdn.jsdelivr.net/gh/chizutodesign/japan-deformed-map@v3.0.2/svg/japan.svg

### HTMLで表示する

自分のWebページのHTMLに次の1行を書くと、地図が画像として表示されます。ファイルを自分のサーバーに置く必要はありません。

```html
<img src="https://cdn.jsdelivr.net/gh/chizutodesign/japan-deformed-map@v3.0.2/svg/japan.svg" alt="日本地図">
```

### JavaScriptで塗り分ける

`<img>` で貼った地図は1枚の絵なので、県ごとに色を変えることはできません。塗り分けたいときはSVGをページ内に展開します。

```js
const svg = await (await fetch("svg/japan.svg")).text();
container.innerHTML = svg;
document.querySelector("#JP-13").setAttribute("fill", "tomato"); // 東京都
```

各都道府県の要素には `id`（JP-01〜JP-47）、`data-name`（日本語名）、`data-romaji` が付いています。動作する例は [examples/](examples/) にあります（スクリーンショット付き。`fetch` を使うため、ファイルを直接開かず `python3 -m http.server` などローカルサーバー経由で開いてください）。

### AIに読ませる

可視化を頼むときは、**使ってほしいSVGのURLを渡してください。** ファイルを指定しないと、AIはグリッドJSONから自前で描こうとして、都道府県が分かれたタイル状になったり、県名のない地図を選んだりします。

```
この地図で都道府県別の森林率を塗り分けてください。
https://cdn.jsdelivr.net/gh/chizutodesign/japan-deformed-map@v3.0.2/svg/japan.svg
```

各都道府県には `id="JP-13"`（ISO 3166-2:JP）が付いているので、AIは統計データと突き合わせて塗り分けられます。県名は白い縁取り付きで入っているため、濃い色で塗っても読めます。

`data/japan.grid.json` は約7.5KBなので、AIが外部URLを取得できない環境ではこちらを貼ってください。ファイル内の `usage` に描画手順を書いてあるので、JSONだけでも県ごとに結合された地図になります。

## データ形式

```jsonc
{
  "grid": { "cols": 28, "rows": 25, "cell_size_mm": 5 },
  "legend": { "a": { "code": "01", "name": "北海道", "romaji": "Hokkaido" }, ... },
  "rows": [
    "......................aaaaaa",
    "......................aaaaaa",
    ...
  ]
}
```

`.` は海、英字1文字が1セルです。文字と都道府県の対応は `legend` を参照してください。

## SVGを再生成する

`svg/` 以下は生成物です。形を変えたいときは `data/japan.grid.json` を編集して、再生成と検証をこの順に実行してください。

```
python3 build/generate.py
python3 build/verify.py
```

`verify.py` は、生成されたSVGが正データと同じセルを占めているか・全座標が整数か・47都道府県のコードが揃っているかを検証します。`OK:` と表示されれば成功です（不一致があれば終了コード1で落ちます）。

SVGを直接編集しないでください。次の再生成で上書きされます。

## ライセンス

地図データと画像（`data/` `svg/` `assets/`）は [CC0 1.0](LICENSE) です。**権利を放棄しています。**
クレジット表示なしで、商用・非商用を問わず自由に利用・改変・再配布できます。許諾を求める必要もありません。

クレジット表示は不要ですが、もし入れていただける場合は下記をお願いします。

```
デフォルメ日本地図 by chizutodesign
https://github.com/chizutodesign/japan-deformed-map
```

スクリプト（`build/` `examples/`）は [MIT License](LICENSE-CODE) です。

## 作者

加藤創 / chizutodesign
https://chizutodesign.com/
