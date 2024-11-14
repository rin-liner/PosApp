import socketio

sio = socketio.Client()

SERVER_IP = "192.168.10.101"
PORT = 5000

@sio.event
def connect():
    print("サーバーに接続されました")

# 新しい注文(呼び出し待ち)
@sio.on('new_order')
def on_new_order(data):
    order_id = data.get('order_id')
    print(f"Received new order ID: {order_id}")

# 完成品ID(呼び出し)
@sio.on('order_call')
def on_order_call(data):
    order_id = data.get('order_id')
    print(f"Received call order ID: {order_id}")

# 注文終了(呼び出し番号削除)
@sio.on('end_order')
def on_end_order(data):
    order_id = data.get('order_id')
    print(f"Received end order ID: {order_id}")

@sio.event
def disconnect():
    print("サーバーから切断されました")

try:
    sio.connect(f"http://{SERVER_IP}:{PORT}") 
    print("サーバーに接続中...")
except socketio.exceptions.ConnectionError as e:
    print(f"サーバーへの接続中にエラーが発生しました: {e}")

# プログラム終了用
input("Press Enter to exit...\n")

sio.disconnect()
