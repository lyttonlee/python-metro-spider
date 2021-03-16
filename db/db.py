import pymysql
import time

db = pymysql.connect(host='39.108.210.247', user='root', passwd='lzr5680545', db='metro', port=3306)

cursor = db.cursor()
