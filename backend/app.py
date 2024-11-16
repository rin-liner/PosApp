# eventletのモンキーパッチを最初に適用
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from sqlalchemy.orm import scoped_session, sessionmaker
from models import db, Product, Order, OrderProduct
from config import DBConfig as Config
import logging
import pytz
from datetime import datetime
from order_call import vvox_test
#from tamasenSerial import Printer
from tamasenSDK import Printer

# Flask アプリの設定
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'
CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:3000", "http://192.168.10.101:3000"]}})
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# ログ設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# データベース初期化
db.init_app(app)
migrate = Migrate(app, db)

# scoped_session を使用したDBセッション管理
with app.app_context():
    db.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.engine))

# Socket.IOイベントの定義
@socketio.on('connect', namespace='/')
def handle_connect():
    client_ip = request.remote_addr  # クライアントのIPアドレスを取得
    logger.info(f"クライアントが接続しました。{client_ip}")
    
@socketio.on('new_order', namespace='/')
def handle_new_order(data):
    logger.debug(f"新しい注文を受信: {data}")
    emit('new_order', data, broadcast=True)

@socketio.on('order_call', namespace='/')
def handle_order_call(data):
    logger.debug(f"注文呼び出しデータを受信: {data}")
    emit('order_call', data, broadcast=True)

@socketio.on('end_order', namespace='/')
def handle_end_order(data):
    logger.debug(f"注文終了データを受信: {data}")
    emit('end_order', data, broadcast=True)

# アプリ終了時にセッションを削除
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Printer クラスの初期化
printer = Printer()

@app.route('/')
def order_page():
    return render_template('order.html')

@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        product_list = [{
            "product_id": product.product_id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "description": product.description,
            "onSale": product.onSale
        } for product in products]
        return jsonify(product_list), 200
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({"message": "Server error"}), 500

@app.route('/product_management', methods=['GET', 'POST'])
def product_management():
    try:
        if request.method == 'POST':
            data = request.json
            logger.debug(f"Received product data: {data}")

            # データのバリデーションを行う
            if not all(key in data for key in ['name', 'price', 'onSale', 'category']):
                logger.error("Invalid product data format received.")
                return jsonify({"message": "Invalid product data format"}), 400

            new_product = Product(
                name=data['name'],
                category=data['category'],
                price=data['price'],
                description=data.get('description', ''),
                onSale=data['onSale']
            )

            db.session.add(new_product)
            db.session.commit()
            return jsonify({"product_id": new_product.product_id, "name": new_product.name, "price": new_product.price, "category": new_product.category, "description": new_product.description, "onSale": new_product.onSale}), 201

        elif request.method == 'GET':
            products = Product.query.all()
            product_list = [{
                "product_id": product.product_id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "description": product.description,
                "onSale": product.onSale
            } for product in products]
            return render_template('product_management.html', products=product_list)
    except Exception as e:
        logger.error(f"Error managing products: {e}")
        return jsonify({"message": "Server error"}), 500

@app.route('/product_management/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.json
        logger.debug(f"Received product update data for product ID {product_id}: {data}")

        product = Product.query.get(product_id)
        if not product:
            logger.error(f"Product with ID {product_id} not found.")
            return jsonify({"message": "Product not found"}), 404

        # 商品の情報を更新
        product.name = data.get('name', product.name)
        product.category = data.get('category', product.category)
        product.price = data.get('price', product.price)
        product.description = data.get('description', product.description)
        product.onSale = data.get('onSale', product.onSale)

        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        return jsonify({"message": "Server error"}), 500

@app.route('/product_management/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            logger.error(f"Product with ID {product_id} not found.")
            return jsonify({"message": "Product not found"}), 404

        # 商品を削除
        db.session.delete(product)
        db.session.commit()

        logger.debug(f"Product with ID {product_id} has been deleted.")
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        return jsonify({"message": "Server error"}), 500


@app.route('/order', methods=['POST'])
def create_order():
    try:
        data = request.json
        logger.debug(f"Received order data: {data}")
        if 'orderL' not in data or not data['orderL']:
            return jsonify({"message": "Invalid order data"}), 400

        # 注文情報をセッションに保存
        session['order_data'] = data
        session.modified = True  # セッションを更新
        logger.debug("Order data has been saved to the session.")

        return jsonify({"message": "Order data saved successfully", "redirect_url": url_for('pay_page')}), 200
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({"message": "Server error"}), 500

@app.route('/orders', methods=['GET'])
def get_incomplete_orders():
    """未完了の注文を取得する"""
    try:
        orders = Order.query.filter_by(is_completed=False).all()
        order_list = [
            {
                'order_id': order.order_id,
                'note': order.note,
                'menuL': [
                    {
                        'name': product.name,
                        'price': product.price,
                        'quantity': op.quantity
                    }
                    for op in OrderProduct.query.filter_by(order_id=order.order_id).all()
                    for product in Product.query.filter_by(product_id=op.product_id).all()
                ]
            }
            for order in orders
        ]
        return jsonify(order_list), 200
    except Exception as e:
        logger.error(f"Error fetching incomplete orders: {e}")
        return jsonify({"message": "Server error"}), 500

@app.route('/pay', methods=['GET', 'POST'])
def pay_page():
    try:
        if request.method == 'POST':
            logger.debug("Processing payment POST request...")
            payment_data = request.json  # JSON データとして取得
            payment_amount = payment_data.get('payment')
            logger.debug(f"Received payment amount: {payment_amount}")

            if not payment_amount or not str(payment_amount).isdigit():
                logger.error("Invalid payment amount received.")
                return render_template('pay.html', order_data=session.get('order_data'), error="Invalid payment amount")

            payment_amount = int(payment_amount)
            logger.debug(f"Parsed payment amount: {payment_amount}")

            order_data = session.get('order_data')
            if not order_data:
                raise ValueError("No order data found in session")
            logger.debug(f"Order data found in session: {order_data}")

            total = order_data['total']
            if payment_amount < total:
                logger.error("Payment amount is less than total order amount.")
                return render_template('pay.html', order_data=order_data, error="支払い金額が不足しています")

            # 注文確定処理
            try:
                # 注文完了トーストの送信
                socketio.emit('order_complete', {'message': '注文完了！レシート印刷中…'})
                logger.debug("Order complete toast emitted.")

                # 注文全体の保存
                total_quantity = sum(item['quantity'] for item in order_data['orderL'])
                order_date = datetime.now(pytz.timezone('Asia/Tokyo'))
                new_order = Order(
                    total_quantity=total_quantity,
                    total_amount=total,
                    note=order_data.get('note', None),
                    created_at=order_date
                )
                db.session.add(new_order)
                db.session.commit()

                logger.debug(f"Order {new_order.order_id} saved to database.")

                # 各商品の注文内容を保存
                for item in order_data['orderL']:
                    product = Product.query.get(item['product_id'])
                    if product:
                        order_product = OrderProduct(
                            order_id=new_order.order_id,
                            product_id=item['product_id'],
                            quantity=item['quantity'],
                            unit_price=product.price  # 注文時点の価格を保存
                        )
                        db.session.add(order_product)

                db.session.commit()
                logger.debug(f"Order items for order {new_order.order_id} saved to database.")

                # 注文情報を厨房画面へ送信
                socketio.emit('new_order', {
                    "order_id": new_order.order_id,
                    "menuL": order_data['menuL'],
                    "note": order_data.get('note', '')
                })

                # レシート印刷
                logger.debug("Attempting to print receipt...")
                printer.print_receipt(
                    order_id=new_order.order_id,
                    orderL=order_data['orderL'],
                    totalL=order_data['totalL'],
                    total=order_data['total'],
                    payment=payment_amount,
                    note=order_data.get('note', ''),
                    menuL=order_data['menuL'],
                    order_date=order_date
                )
                logger.debug("Receipt printing completed.")

                # 注文データをセッションから削除
                session.pop('order_data', None)
                logger.debug("Order data removed from session.")

                return redirect(url_for('order_page'))
            except Exception as e:
                logger.error(f"Error while processing order confirmation or printing receipt: {e}")
                db.session.rollback()
                return render_template('pay.html', order_data=order_data, error="サーバーエラーが発生しました。再度お試しください。")
        else:
            logger.debug("Handling GET request for pay page.")
            order_data = session.get('order_data')
            if not order_data:
                logger.error("No order data found in session.")
                return render_template('pay.html', error="注文データが見つかりませんでした。再度お試しください。")
            logger.debug(f"Rendering pay page with order data: {order_data}")
            return render_template('pay.html', order_data=order_data)
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return render_template('pay.html', error=str(e))
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        return render_template('pay.html', error="サーバーエラーが発生しました。")

@app.route('/current_order', methods=['GET'])
def get_current_order():
    try:
        order_data = session.get('order_data')
        if not order_data:
            return jsonify({"message": "No order data found in session"}), 400
        return jsonify(order_data), 200
    except Exception as e:
        logger.error(f"Error getting current order: {e}")
        return jsonify({"message": "Server error"}), 500
    
@app.route('/order_history', methods=['GET'])
def order_history():
    try:
        orders = Order.query.all()
        order_history = []
        total_items_sold = 0  # 合計商品の個数を保持する変数
        total_sales_amount = 0  # 合計販売額を保持する変数

        for order in orders:
            total_price = 0  # 各注文の合計金額
            order_data = {
                "order_id": order.order_id,
                "created_at": order.created_at.isoformat(),
                "total_quantity": order.total_quantity,
                "note": order.note,
                "products": []
            }

            # 注文に関連する商品情報を取得
            order_products = OrderProduct.query.filter_by(order_id=order.order_id).all()
            for order_product in order_products:
                product = Product.query.get(order_product.product_id)
                if product:
                    product_total_price = order_product.unit_price * order_product.quantity
                    total_price += product_total_price  # 注文の合計金額に追加
                    total_items_sold += order_product.quantity  # 合計商品の個数を加算

                    order_data["products"].append({
                        "name": product.name,
                        "unit_price": order_product.unit_price,
                        "quantity": order_product.quantity,
                        "total_price": product_total_price
                    })

            total_sales_amount += total_price  # 総販売額に注文の合計金額を加算
            order_data["total_price"] = total_price
            order_history.append(order_data)

        # 合計商品の個数と販売額をレスポンスに含める
        return jsonify({
            "order_history": order_history,
            "total_items_sold": total_items_sold,
            "total_sales_amount": total_sales_amount
        }), 200

    except Exception as e:
        logger.error(f"Error getting order history: {e}")
        return jsonify({"message": "Server error"}), 500


@app.route('/product_count', methods=['GET'])
def product_count():
    try:
        # データベースから商品ごとの売上数を集計するクエリ
        results = db.session.query(
            Product.product_id,
            Product.name,
            db.func.sum(OrderProduct.quantity).label('sold')
        ).join(OrderProduct, Product.product_id == OrderProduct.product_id).group_by(
            Product.product_id, Product.name
        ).all()

        # 集計結果をリストとして返す
        sales_summary = []
        for row in results:
            sales_summary.append({
                'product_id': row.product_id,
                'product_name': row.name,
                'sold': row.sold
            })

        return jsonify(sales_summary), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve sales data: {str(e)}'}), 500
    
@app.route('/order_call', methods=['POST'])
def order_call():
    try:
        data = request.json
        order_id = data.get('order_id')
        text = data.get('text', '')

        # 注文IDの確認
        if not order_id:
            logger.error("No order ID provided")
            return jsonify({"error": "No order ID provided"}), 400

        # 注文を取得して完了フラグを更新
        order = Order.query.get(order_id)
        if not order:
            logger.error(f"Order with ID {order_id} not found")
            return jsonify({"error": f"Order with ID {order_id} not found"}), 404

        order.is_completed = True  # 完了フラグを更新
        db.session.commit()
        logger.debug(f"Order {order_id} marked as completed")

        # 音声合成の実行
        if text:
            logger.debug(f"Order call with text: {text}")
            vvox_test(text)  # 音声合成を呼び出す
        else:
            logger.error("No text provided for order call")
            return jsonify({"error": "No text provided"}), 400

        return jsonify({"message": f"Order {order_id} call initiated"}), 200
    except Exception as e:
        logger.error(f"Error in order call: {e}")
        db.session.rollback()  # エラー時にはロールバック
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
