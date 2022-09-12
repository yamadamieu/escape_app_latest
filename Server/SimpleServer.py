from cmath import isnan
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

#災害のリスト
disaster_list = ["flood","landslide","storm_surge","earthquake","tsunami","fire","inland_flood","volcano"]

#災害を指定して格納する関数
def disaster_select(datalist,num):
    if num == 0:
        datalist = datalist.select().where(DataModel.flood == 1)
    elif num == 1:
        datalist = datalist.select().where(DataModel.landslide == 1)
    elif num == 2:
        datalist = datalist.select().where(DataModel.storm_surge == 1)
    elif num == 3:
        datalist = datalist.select().where(DataModel.earthquake == 1)
    elif num == 4:
        datalist = datalist.select().where(DataModel.tsunami == 1)       
    elif num == 5:
        datalist = datalist.select().where(DataModel.fire == 1)
    elif num == 6:
        datalist = datalist.select().where(DataModel.inland_flood == 1)
    else:
        datalist = datalist.select().where(DataModel.volcano == 1)
    return datalist





#現在位置を所得する関数
def get_locate():
    geo_request_url = 'https://get.geojs.io/v1/ip/geo.json'
    geo_data = requests.get(geo_request_url).json()
    ido = geo_data['latitude']
    keido = geo_data['longitude']
    return ido,keido


#避難所の絞り込み
@app.route('/select',methods=['POST'])
def select():
    ido = request.form.get('緯度')
    keido = request.form.get('経度')
    now_Station = (ido, keido)
    dis_list = []
    #　災害の指定されたものをリストに保存：後で関数にする
    if request.form.get('a') != None:
        dis_list.append(int(request.form.get('a')))
    if request.form.get('b') != None:
        dis_list.append(int(request.form.get('b')))
    if request.form.get('c') != None:
        dis_list.append(int(request.form.get('c')))
    if request.form.get('d') != None:
        dis_list.append(int(request.form.get('d')))
    if request.form.get('e') != None:
        dis_list.append(int(request.form.get('e')))
    if request.form.get('f') != None:
        dis_list.append(int(request.form.get('f')))
    if request.form.get('g') != None:
        dis_list.append(int(request.form.get('g')))
    if request.form.get('h') != None:
        dis_list.append(int(request.form.get('h')))
    if request.form.get('i') != None:
        dis_list.append(int(request.form.get('i')))

    datalist = DataModel
    # 災害から避難所絞り込み　
    for _ in range(len(dis_list)):
        d = dis_list.pop()
        datalist = disaster_select(datalist,d)
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