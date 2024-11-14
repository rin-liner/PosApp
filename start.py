import os
import sys
import requests
import subprocess
from sqlalchemy import create_engine
from time import sleep

# Step 1: localhost:50021 のレスポンス確認
def check_localhost_response():
    try:
        response = requests.get("http://localhost:50021")
        if response.status_code == 200:
            print("localhost:50021 is responding correctly.")
        else:
            print("Error: localhost:50021 did not return a 200 status.")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to localhost:50021. Details: {e}")
        sys.exit(1)

# Step 2: データベースへのアクセス確認
def check_database_connection():
    try:
        # SQLAlchemyエンジンを使用してデータベースに接続
        engine = create_engine(os.getenv("DATABASE_URL", "mysql+pymysql://posDB:posnextgen@127.0.0.1/postest"))
        connection = engine.connect()
        print("Database connection successful.")
        connection.close()
    except Exception as e:
        print(f"Error: Could not connect to the database. Details: {e}")
        sys.exit(1)

# Step 3: Flaskアプリケーションの起動（別コンソール）
def start_backend():
    print("Starting backend in a new console...")
    if os.name == 'nt':  # Windows
        subprocess.Popen(["start", "cmd", "/k", "python", "backend/app.py"], shell=True)
    elif os.name == 'posix':  # macOS/Linux
        subprocess.Popen(["gnome-terminal", "--", "python3", "backend/app.py"])
    sleep(5)  # バックエンドが安定するまでの待機

# Step 4: フロントエンドの起動（別コンソール）
def start_frontend():
    print("Starting frontend in a new console...")
    frontend_path = os.path.join("frontend", "Client", "my-app")
    if os.name == 'nt':  # Windows
        subprocess.Popen(["start", "cmd", "/k", "npm", "start", "--host", "0.0.0.0"], cwd=frontend_path, shell=True)
    elif os.name == 'posix':  # macOS/Linux
        subprocess.Popen(["gnome-terminal", "--", "npm", "start", "--host", "0.0.0.0"], cwd=frontend_path)

# メイン処理
if __name__ == "__main__":
    # localhostとDBへのアクセス確認
    check_localhost_response()
    check_database_connection()
    
    # BackendとFrontendを別コンソールで起動
    start_backend()
    start_frontend()
