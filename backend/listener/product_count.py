import requests
import time
from datetime import datetime

# サーバーの設定
SERVER_IP = '192.168.10.101'
PORT = '5000'

def get_sales_summary():
    try:
        response = requests.get(f'http://{SERVER_IP}:{PORT}/product_count')
        if response.status_code == 200:
            results = response.json()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total = 0
            print(f"=== 売り上げ集計 ({current_time}) ===")
            for row in results:
                product_id = int(row['product_id'])
                product_name = row['product_name']
                sold = int(row['sold'])
                print(f"商品ID: {product_id}, 商品名: {product_name}, 売上数: {sold}")
                total += sold
            print(f"総売上個数: {total}")
            print("===========================")
        else:
            print(f"売り上げデータの取得に失敗しました: {response.status_code}")

    except requests.RequestException as e:
        print(f"エンドポイントへの接続中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    while True:
        # 売り上げ集計を1分ごとに取得
        get_sales_summary()
        time.sleep(60)
