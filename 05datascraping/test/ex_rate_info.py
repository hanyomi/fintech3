import re
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from io import StringIO
from sqlalchemy import create_engine, text
import pymysql
pymysql.install_as_MySQLdb()
from dbio import db_connect, to_db

def new_cols(df):
    result = []
    for col in df.columns:
        if col[0] == col[1] == col[2]:
            result.append(col[0].replace(" ", "_"))
        elif col[1] == col[2]:
            result.append("_".join(col[:2]).replace(" ", "_"))
        else:
            result.append("_".join(col).replace(" ", "_"))
    return result

def get_ex_rate_data(db_name, table_name, date):
    # 1995년 1월 3일부터 오늘 날짜까지 생성
    date = datetime.today() - timedelta(days=1)
    date = f"{date.date()}"
    url = "https://www.kebhana.com/cms/rate/wpfxd651_01i_01.do"
    payload = dict(ajax="true", tmpInqStrDt=f"{date}", pbldDvCd=3, inqStrDt=f"{date}".replace("-", ""), inqKindCd=1, requestTarget="searchContentDiv")
    r = requests.post(url, data=payload)
    df = pd.read_html(StringIO(r.text))[0]
    df.columns = new_cols(df)
    df.insert(0, '날짜', f"{date}")
    to_db(db_name, table_name, df)
    return print(f"{date} 환율 데이터 수집 완료")

def main():
    db_name = "ex_rate"
    table_name= "ex_rate_table"
    date = datetime.today() - timedelta(days=1)
    date = f"{date.date()}"

    try:
        conn = db_connect(db_name)
        conn.execute(text(f"select * from {table_name} where 날짜 = {date}"))
        print(f"{date} 환율 데이터가 DB에 이미 있습니다.")
    except:
        get_ex_rate_data(db_name, table_name, date)
        print(f"{date} 환율 데이터가 없어 데이터를 수집합니다.")


if __name__ == "__main__":
    main()


