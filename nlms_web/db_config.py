# db_config.py

import mysql.connector
from flask import g

def get_db_connection():
    """
    建立并返回一个新的 MySQL 连接。
    请根据你的环境修改 host、user、password、database 等参数。
    """
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="group8",
        database="nlms",
   
    )
    return conn


