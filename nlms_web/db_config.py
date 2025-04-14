# db_config.py

import mysql.connector
from flask import g

def get_db_connection():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="group8",
        database="nlms",
   
    )
    return conn


