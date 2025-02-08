# rta_chart_app
# RTA チャート管理アプリケーション

## 概要
RTAのルート管理のためのWebアプリケーションです。チャートとステップを作成・編集・削除し、効率的にRTAのルートを管理することができます。

## 主な機能
- チャートの作成・編集・削除
- ステップの作成・編集・削除  
- ドラッグ&ドロップによるステップの順序変更
- 画像のアップロード機能
- メモ機能

## 技術スタック
- バックエンド: Python (Flask)
- データベース: SQLite
- フロントエンド: HTML, CSS, JavaScript
- ORM: SQLAlchemy

## セットアップ方法
1. 必要なパッケージのインストール:
```bash
pip install flask flask-sqlalchemy werkzeug
```

2. アプリケーションの起動:

```bash
python app.py
```

3. ブラウザで以下のURLにアクセス:
http://localhost:5000

## ディレクトリ構造

```text
rta_chart_app/
├── app.py
├── static/
│   ├── style.css
│   ├── script.js
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── chart_list.html
│   ├── chart_detail.html
│   ├── chart_form.html
│   ├── step_detail.html
│   └── step_form.html
└── rta_chart.db
```


## データベース構造
### Charts テーブル
- id: 主キー
- title: チャートのタイトル
- category: チャートのカテゴリ

### Steps テーブル
- id: 主キー
- chart_id: 外部キー（Chartsテーブルへの参照）
- order: ステップの順序
- title: ステップのタイトル
- memo: ステップのメモ
- image_path: アップロードされた画像のパス

## 注意事項
- アップロードできる画像の最大サイズは16MBです
- 対応している画像形式: PNG, JPG, JPEG, GIF
- アップロードされた画像は `static/uploads` ディレクトリに保存されます

## ライセンス
MITライセンス