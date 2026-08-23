# 使用例

いずれも `fetch()` でデータを読み込むため、**HTMLファイルを直接開いても動きません**。ブラウザは `file://` で開いたページからのファイル読み込みをセキュリティ上ブロックします（コンソールに `blocked by CORS policy` と出ます）。

リポジトリのルートでローカルサーバーを起動してから開いてください。

```
python3 -m http.server
```

→ http://localhost:8000/examples/css-grid.html

## css-grid.html

`data/japan.grid.json` を読み込み、CSS Grid で1セル1マスとして描画します。セルにマウスを乗せると県名が表示されます。SVGを使わずJSONだけで地図を描く例です。

![css-grid.html の実行画面](css-grid.png)

## svg-choropleth.html

`dist/japan-rounded.svg` を読み込んでページに展開し、都道府県ごとに値に応じた色を塗ります（コロプレス図）。`id="JP-13"` のような識別子を使って塗り分けます。

![svg-choropleth.html の実行画面](svg-choropleth.png)
