# init_db.py
from flask import Flask
from models import db, Product, Order, OrderProduct
from config import DBConfig as Config

def initialize_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # データベースのテーブルをすべて削除してから作成する（必要に応じて削除を省略）
        db.drop_all()
        db.create_all()
        
        print("データベースの初期化が完了しました。")

if __name__ == "__main__":
    initialize_db()
