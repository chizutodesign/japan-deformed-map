# 使用例

いずれも `fetch()` でデータを読み込むため、**HTMLファイルを直接開いても動きません**。ブラウザは `file://` で開いたページからのファイル読み込みをセキュリティ上ブロックします（コンソールに `blocked by CORS policy` と出ます）。

リポジトリのルートでローカルサーバーを起動してから開いてください。

```
python3 -m http.server
```

→ http://localhost:8000/examples/css-grid.html

## css-grid.html

`data/japan.grid.json` だけで地図を描く例です。1セル=1要素で並べたうえで、隣のセルが別の県のときだけ境界線を引いて、都道府県として結合して見えるようにしています。マウスを乗せるとその県全体が明るくなり、県名が表示されます。

単に地図を表示・塗り分けたいだけなら、都道府県が結合済みの `dist/japan.svg` を使う方が簡単です。

![css-grid.html の実行画面](css-grid.png)

## svg-choropleth.html

`data/japan.grid.json` から値を作り、`dist/japan-rounded.svg` を展開して `id="JP-13"` のような識別子で塗り分けます（コロプレス図）。「値の算出はJSON、描画はSVG」という想定どおりの組み合わせの例です。

各県には県名と数値を直接置いています。デフォルメ地図は矩形なのでラベル領域が確保でき、地理に詳しくない人でもどこがどの県か分かります。

題材は県名の画数合計です。塗り分けの手順を示すための無害な題材で、何かの優劣を表すものではありません。

![svg-choropleth.html の実行画面](svg-choropleth.png)
