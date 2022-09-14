from ast import Break
from http.client import OK
from flask import Flask,render_template,jsonify,make_response,abort,request,url_for
import peewee
import json
#位置情報所得用
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

#　日本の経度緯度の範囲の最大直径
MAX_DIS = 32

def range_decide(ido,keido,N,direction):
    if int(direction) in [0,1,3,4,5,6]:
        top = float(ido) + N
    else:
        top = float(ido)
    if int(direction) in [0,2,3,4,7,8]:
        bottom = float(ido) - N
    else:
        bottom = float(ido) 
    if int(direction) in [0,1,2,3,6,8]:
        right = float(keido) + N
    else:
        right = float(keido)
    if int(direction) in [0,1,2,4,5,7]:
        left = float(keido) - N
    else:
        left = float(keido)
    print("範囲関数")
    return top,bottom,right,left

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

#避難所検索結果
@app.route('/result',methods=['POST'])
def result():
    ido = request.form.get('latitude')
    keido = request.form.get('longitude')
    direction = request.form.get('direction')
    now_Station = (ido, keido)
    print(direction)

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
        top,bottom,right,left = range_decide(ido,keido,N,direction)
        for v in datalist:
            # top = float(ido) + N
            # bottom = float(ido) - N
            # right = float(keido) + N
            # left = float(keido) - N
            # top,bottom,right,left = range_decide(ido,keido,N,direction)
            if top > v.latitude and bottom < v.latitude:
                if right > v.longitude and left < v.longitude:
                    v_Station = (v.latitude, v.longitude)
                    dis = format(geodesic(now_Station, v_Station).km,'.2f') #現在地と避難所の距離を小数点以下2桁で計算
                    append_list=[v.name,dis]   
                    result_in.append(append_list)
        print(N)
        print(top)
        print(bottom)
        print(right)
        print(left)
        N = N + 0.01
        result = result_in
        print(len(result))
        if N > MAX_DIS:
            break


    if len(result) >= 1:
        #距離でソート
        result = sorted(result, key=lambda x: x[1])
    else:
        result.append(["見つかりませんでした",0])

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
@app.route('/')
def index():
    # トップページを表示
    return render_template('index.html')

####################################################################

# サービス起動
if __name__ == '__main__':
    app.run(debug=True)