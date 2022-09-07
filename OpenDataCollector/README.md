# OpenDataCollector
オープンデータ収集ツール

# 概要
  
 オープンデータを収集／集計して、指定のWebデータベースに投稿するアプリです。
  
 三重県オープンデータライブラリからのデータ収集を例として実装しています。

# 導入方法
  
 Pythonが動作するPC上で実行します。
  
# ソースのチェックアウト
```
git clone https://github.com/tt-hasegawa/OpenDataCollector.git
```

# テスト用Webサーバの起動
Serverフォルダにてコマンドプロンプト／シェルを開く

以下のコマンドを実行して関連ライブラリをインストールする
```
pip install -r requirements.txt
```
以下のコマンドを実行し、Webサーバを起動する。
```
python SimpleServer.py
``` 

```
 * Running on http://0.0.0.0:3000/ (Press CTRL+C to quit)
```
と表示されたら、サーバ起動OK。

# データ収集
Clientフォルダにてコマンドプロンプト／シェルを開く
以下のコマンドを実行して関連ライブラリをインストールする
```
pip install -r requirements.txt
```

```
python DoCollect.py
``` 

Webブラウザでhttp://localhost:3000
を開いて、グラフにデータが表示されたらOK。

