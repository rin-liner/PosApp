# README

`pip install -r requirements.txt`

ローカルネットワーク内の端末を想定しています。

それぞれうごくのでうまく改造してください。

posシステムが動いてないときや、PCをwifiに入れてないときもあるから、テストするときは伝えてくれると嬉しいです

## ローカルネットワーク

>[!TIP]
>ルータは1408の私のデスクに

- SSID : rinpos2G
- password : posnextgen

>[!WARNING]
>いんたーねっとに繋げてないので注意(pip不可)

## ファイル

### order_listener.py

`@sio.on('new_order')`はpay画面の注文確定ボタン（料金支払いボタン）を押した瞬間に送られます。 \
呼び出し待ちの番号の表示に使ってください。(マクド画面の右のグレーの数字)
厨房画面に送るデータを引っこ抜いてるので、\
`{'order_id': 124, 'menuL': [{'name': 'normal', 'price': 250, 'quantity': 1}], 'note': None}` \
こんな感じに取れます。

`@sio.on('order_call')`は厨房画面の一度目のタップで送信されます。同時にずんだもんが呼び出します。 \
呼び出し番号のメイン部分でしょう。

`@sio.on('end_order')`は厨房画面二度目のタップで送信されます。厨房画面からorderが消えると送られる感じ。

### product_count.py

エンドポイント`/product_count`を叩きます。このエンドポイントではクリエを叩いて売上個数データを取得しています。

## DB

>[!IMPORTANT]
>いろいろ書いたけど外からMySQLたたけないのでproduct_countのエンドポイントを作りました。
>
>よってこの下は参考程度に

```python
DB_CONFIG = {
    'user': 'posDB',
    'password': 'posnextgen',
    'host': '192.168.10.101',
    'port': '3306',
    'database': 'postest',
    # 'postest':test環境用
    # 'posprod':本番環境用
}
```

本番当日のみposprodを使用する予定です。posprod内の商品データは以下にする予定

|product_id|product_name|
|:---:|:---:|
|1|normal|
|2|DX|
|3|GAMING|

そのほかDB

### order

| Field          | Type        | Null | Key  | Default | Extra          |
| -------------- | ----------- | ---- | ---- | ------- | -------------- |
| order_id       | int         | NO   | PRI  | NULL    | auto_increment |
| created_at     | datetime    | YES  |      | NULL    |                |
| total_quantity | int         | NO   |      | NULL    |                |
| total_amount   | int         | NO   |      | NULL    |                |
| note           | varchar(100)| YES  |      | NULL    |                |

### order_product

| Field      | Type | Null | Key | Default | Extra |
| ---------- | ---- | ---- | --- | ------- | ----- |
| order_id   | int  | NO   | PRI | NULL    |       |
| product_id | int  | NO   | PRI | NULL    |       |
| quantity   | int  | NO   |     | NULL    |       |
| unit_price | int  | NO   |     | NULL    |       |

インデックスに`product_id`使用

### product

| Field       | Type         | Null | Key  | Default | Extra          |
| ----------- | ------------ | ---- | ---- | ------- | -------------- |
| product_id  | int          | NO   | PRI  | NULL    | auto_increment |
| name        | varchar(100) | NO   |      | NULL    |                |
| category    | varchar(50)  | NO   |      | NULL    |                |
| price       | int          | NO   |      | NULL    |                |
| description | text         | YES  |      | NULL    |                |
| onSale      | tinyint(1)   | YES  |      | NULL    |                |

- `category`:使用してない。 `menu`突っ込んでる。
- `description`:使用してない。 説明書く予定だった。
