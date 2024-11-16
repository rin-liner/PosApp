import os
import sys
import requests
import subprocess
from sqlalchemy import create_engine
from time import sleep
from pathlib import Path
sys.path.append(str(Path(__file__).parent/"backend"))
from backend.config import DBConfig, BTConfig, SerialConfig, VVConfig
from backend.csjwindowspossdk import ESCPOSConst, ESCPOSPrinter

# Step 1: localhost:50021 のレスポンス確認
def check_localhost_response():
    try:
        SERVER_URL = f"http://{VVConfig.HOST}:{VVConfig.PORT}"
        response = requests.get(SERVER_URL)
        if response.status_code == 200:
            print(f"{SERVER_URL} is responding correctly.")
        else:
            print(f"Error: {SERVER_URL} did not return a 200 status.")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to {SERVER_URL}. Details: {e}")
        sys.exit(1)

# Step 2: データベースへのアクセス確認
def check_database_connection():
    try:
        # SQLAlchemyエンジンを使用してデータベースに接続
        engine = create_engine(DBConfig.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        print("Database connection successful.")
        connection.close()
    except Exception as e:
        print(f"Error: Could not connect to the database. Details: {e}")
        sys.exit(1)

# Step 4: プリンター接続確認
def check_printer_connection():
    printer = ESCPOSPrinter()
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts and printer.Connect(BTConfig.CONTENT_TYPE, BTConfig.ADDR) != ESCPOSConst.CMP_SUCCESS:
        printer.Disconnect()
        sleep(3)
        print("Reconnecting...")
        attempts += 1
    if attempts == max_attempts:
        print("Failed to connect after 3 attempts.")
        printer.Disconnect()
        sys.exit(1)
    else:
        print("Printer connection successful.")
        printer.Disconnect()

# Step 4: Flaskアプリケーションの起動（別コンソール）
def start_backend():
    print("Starting backend in a new console...")
    if os.name == 'nt':  # Windows
        subprocess.Popen(["start", "cmd", "/k", "python", "backend/app.py"], shell=True)
    elif os.name == 'posix':  # macOS/Linux
        subprocess.Popen(["gnome-terminal", "--", "python3", "backend/app.py"])
    sleep(5)  # バックエンドが安定するまでの待機

# Step 5: フロントエンドの起動（別コンソール）
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
    check_printer_connection()
    
    # BackendとFrontendを別コンソールで起動
    start_backend()
    start_frontend()
