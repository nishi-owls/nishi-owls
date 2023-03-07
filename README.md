# OWLS Homepage

## 環境構築

当サイトは [Jekyll](https://jekyllrb-ja.github.io/) で構築されています。
ローカル環境で実行するには Jekyll をインストールしてください。

[Jekyllのチュートリアル](https://jekyllrb-ja.github.io/docs/step-by-step/01-setup/) のステップ1から10全てを実施するのを推奨します。

尚、rbenv使用時は `/.ruby-version` のversion指定が反映されますが、rbenvを使用しない環境では気を付けてください。
特にデフォルトではrbenvが使用できないWindowsでは要注意です。

## ローカル環境でサイトを実行する

```
(rbenv exec) bundle exec jekyll serve
```

`--drafts` オプションを追加することで、 `_drafts` ディレクトリ以下のドラフトコンテンツ（トピックス以下に展開されるもの）を見ることができます。

## 外部リソースのメモ

* Facebook logo (assets/images/facebook.png)
  - From https://ja.facebookbrand.com/facebookapp/
* Twitter logo (assets/images/twitter.png)
  - From https://about.twitter.com/en/who-we-are/brand-toolkit
* Instagram logo (assets/images/instagram.png)
  - From https://en.facebookbrand.com/instagram/assets/instagram?audience=instagram-landing
* Tocca.js （スワイプ検出用。軽量のため採用。）
  - From https://github.com/GianlucaGuarini/Tocca.js