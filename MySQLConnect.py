import pymysql
import os
from dotenv import load_dotenv
import json

load_dotenv()
host=os.getenv("DB_HOST")
user=os.getenv("DB_USER")
name=os.getenv("DB_NAME")

db = pymysql.connect(host=host,user=user,database=name)

resultDict=[]

with db:
    with db.cursor() as cursor:
        sql=f"SELECT * FROM pruebas"
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            rowDict={
                'id':row[0],
                'mainName':row[1],
                'domain':row[2]
            }
            resultDict.append(rowDict)

