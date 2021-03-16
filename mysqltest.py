import pymysql
import time

db = pymysql.connect(host='39.108.210.247', user='root', passwd='lzr5680545', db='metro', port=3306)

cursor = db.cursor()

info = {
  'city': '成都',
  'date': '2021年1月23日',
  'passenger': '478'
}

try:
  sql = "select * from city_metro where city='%s'" % (info['city'])
  # sql = "select * from city_metro"
  cursor.execute(sql)
  res = cursor.fetchall()
  print(res)
except:
  print('no data exist')
  # record_timestamp = int(time.mktime(time.strptime(info['date'], '%Y年%m月%d日')))
  # sql = "insert into city_metro (city, date, passenger, timestamp) values ('%s', '%s', '%s', %d)" % (info['city'], info['date'], info['passenger'], record_timestamp)
  # cursor.execute(sql)
  # db.commit()