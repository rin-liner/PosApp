# config.py
import os
import __relimport
from csjwindowspossdk import ESCPOSConst


class DBConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://posDB:posnextgen@127.0.0.1/postest")
    # postest:test用 posprod:本番用
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class BTConfig:
    CONTENT_TYPE = ESCPOSConst.CMP_PORT_Bluetooth
    ADDR = "00:01:90:DF:CD:AA"

class SerialConfig:
    PORT = "COM4"
    BAUDRATE = 9600

class VVConfig:
    HOST = "127.0.0.1"
    PORT = 50021
