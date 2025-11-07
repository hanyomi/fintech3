import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
from sqlalchemy import create_engine, text
import pymysql
pymysql.install_as_MySQLdb()
load_dotenv()

db_id = os.getenv("id")
db_pw = os.getenv("pw")
addr = os.getenv("addr")
port = os.getenv("port")

def db_connect(dbname):
    check_engine = create_engine(f"mysql+pymysql://{db_id}:{db_pw}@{addr}:{port}")
    with check_engine.connect() as conn:
        conn.execute(text(f"create database if not exists {dbname}"))
        print(f"{dbname} 데이터베이스 생성/확인 완료")
    
    engine = create_engine(f"mysql+pymysql://{db_id}:{db_pw}@{addr}:{port}/{dbname}")
    conn = engine.connect()
    return conn


def load_data(dbname, table_name):
    conn = db_connect(dbname)
    data = pd.read_sql(table_name, con=conn)
    conn.close()
    return data        

def to_db(dbname, table_name, df):
    conn = db_connect(dbname)
    df.to_sql(table_name, con=conn, index=False, if_exists="append")
    conn.close()
    return
    

