import pandas as pd
import requests
import json

# 読込先URL
url='https://hinan.gsi.go.jp/hinanjocjp/hinanbasho/downloadAllCsv.php'

proxies = {
    "http": None,
    "https": None,
}

# 列名の定義
cols = ["name","adress","flood","landslide","storm_surge","earthquake","tsunami","fire","inland_flood","volcano","latitude","longitude"]

#dfの宣言(urlのエクセルを読み込んでいる)
df=pd.read_csv(url,          # 読込先URL
                skipfooter=0,   # 読み飛ばすフッター行。この場合、最後2行は読み飛ばす
                usecols=[3,4,5,6,7,8,9,10,11,12,14,15],   # 読み込む列番号を指定
                names = cols    # 列名の設定
                )
                
print(1111111)
print(df)
print(len(df))
# 1行ごと取り出しfor文　→JSON化してPOST
for row in df.itertuples():
  #計と県は除外
    
  jsonData = {
          "number":row[0],
          "name":str(row[1]),
          "adress":str(row[2]),
          "flood":row[3],
          "landslide":row[4],
          "storm_surge":row[5],
          "earthquake":row[6],
          "tsunami":row[7],
          "fire":row[8],
          "inland_flood":row[9],
          "volcano":row[10],
          "latitude":row[11],
          "longitude":row[12]
        }
  print(jsonData)
        #addDataにpost jsonという変数
  print("実行中ーー")
  #サーバにデータを送る
  response = requests.post('http://127.0.0.1:3000/addData/' , json=json.dumps(jsonData),proxies=proxies)
  print(response)
print("Docollect_success")
