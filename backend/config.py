# config.py
import os
import __relimport
from csjwindowspossdk import ESCPOSConst

CONTENT_TYPE = ESCPOSConst.CMP_PORT_Bluetooth
ADDR = "00:01:90:df:cd:aa"
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://posDB:posnextgen@127.0.0.1/postest")
    # postest:test用 posprod:本番用
    SQLALCHEMY_TRACK_MODIFICATIONS = False
