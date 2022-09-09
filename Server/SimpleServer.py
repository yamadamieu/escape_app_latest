from flask import Flask,render_template,jsonify,make_response,abort,request,url_for
import peewee
import json
#位置情報所得用
import requests
from geopy.distance import geodesic

# 初期設定
app = Flask(__name__)

# SQLiteDBの生成
db= peewee.SqliteDatabase("data.db")

################################################################################
# データモデルクラス
class DataModel(peewee.Model):
    number = peewee.IntegerField(null=True,default=0)
    name = peewee.TextField()
    adress = peewee.TextField()
    flood = peewee.IntegerField(null=True,default=0)
    landslide = peewee.IntegerField(null=True,default=0)
    storm_surge = peewee.IntegerField(null=True,default=0)
    earthquake = peewee.IntegerField(null=True,default=0)
    tsunami = peewee.IntegerField(null=True,default=0)
    fire = peewee.IntegerField(null=True,default=0)
    inland_flood = peewee.IntegerField(null=True,default=0)
    volcano = peewee.IntegerField(null=True,default=0)
    latitude = peewee.FloatField(null=True,default=0.0)
    longitude = peewee.FloatField(null=True,default=0.0)

    class Meta:
        database = db
################################################################################

# テーブルの作成
db.create_tables([DataModel])

#現在位置を所得する関数
def get_locate():
    geo_request_url = 'https://get.geojs.io/v1/ip/geo.json'
    geo_data = requests.get(geo_request_url).json()
    ido = geo_data['latitude']
    keido = geo_data['longitude']
    return ido,keido

# API実装
# データ取得API→Chart.jsで参照するのに使う
@app.route('/getData/', methods=['GET'])
def get_Ventilations():
    print("dooooo_getdata")
    #データベースからデータを取ってくる
    #都市順に並べ替え
    datalist = DataModel.select().order_by(DataModel.city)
    # グラフ描画用データセットを準備する。
    labels = []
    dataset = {
            'data':[]
            }
    # データを読み込んで、グラフ用に編集しながら追加していく。
    #ラベルに都市名、データに今の値
    for v in datalist:
        labels.append(v.city)
        dataset['data'].append(v.now)

    # JSON形式で戻り値を返すために整形
    result = {
            "labels":labels,
            "datasets":[dataset]}
    print(result)
    #jsonファイルを送るjsonify
    #make_responseで返す
    return make_response(jsonify(result))

#避難所の絞り込み
@app.route('/select',methods=['POST'])
def select():
    ido = request.form.get('緯度')
    keido = request.form.get('経度')
    now_Station = (ido, keido)
    datalist = DataModel
    result = []
    N = 0.01
    limit = 10 #探す件数
    while len(result) < limit:
        result_in = []
        for v in datalist:
            top = float(ido) + N
            bottom = float(ido) - N
            right = float(keido) + N
            left = float(keido) - N
            if top > v.latitude and bottom < v.latitude:
                if right > v.longitude and left < v.longitude:
                    v_Station = (v.latitude, v.longitude)
                    dis = geodesic(now_Station, v_Station).km
                    append_list=[v.name,dis]   
                    result_in.append(append_list)

        N = N + 0.01
        result = result_in

    #距離でソート
    result = sorted(result, key=lambda x: x[1])

    #上位10個に
    result = result[0:limit]
    return render_template('result.html',result=result)





# 登録API POSTのみ受付
@app.route('/addData/', methods=['POST'])
def addData():
    # POSTされたJSONデータからキーを元にデータ取得
    print(request.json)
    # jsonデータのロード
    jsonData = json.loads(request.json)
    # 確認
    print(jsonData)

    #vはDataModelクラスのインスタンス
    v = DataModel(
                number=jsonData["number"],
                name=jsonData["name"],
                adress=jsonData["adress"],
                flood=jsonData["flood"],
                landslide=jsonData["landslide"],
                storm_surge=jsonData["storm_surge"],
                earthquake=jsonData["earthquake"],
                tsunami=jsonData["tsunami"],
                fire=jsonData["fire"],
                inland_flood=jsonData["inland_flood"],
                volcano=jsonData["volcano"],
                latitude=jsonData["latitude"],
                longitude=jsonData["longitude"]
                )


    # データを保存
    v.save()
    print("doooo_adddata")
    print(v)
    return "ok"

#####################################################################
# ページ遷移
# 初期ページ
@app.route('/',methods=['GET','POST'])
def index():
    #経度と緯度を保持
    if request.method == 'POST':
        ido = request.form.get('緯度')
        keido = request.form.get('経度')
    #GETなら緯度経度を自動所得
    else:
        ido,keido = get_locate()
    # トップページを表示
    return render_template('index.html',ido=ido,keido=keido)

####################################################################
#位置情報を自動で取得
@app.route('/adress')
def adress():
    ido,keido = get_locate()
    # トップページを表示
    return render_template('index.html',ido=ido,keido=keido)



# サービス起動
if __name__ == '__main__':
    app.run(debug=True)