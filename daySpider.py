#coding=utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import pymysql
# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

db = pymysql.connect(host='39.108.210.247', user='root', passwd='lzr5680545', db='metro', port=3306)

cur = db.cursor()


# 不打开浏览器窗口运行
option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome(options=option)
driver.set_window_size(1200, 800)

citys = [
  {
    'name': '西安',
    'url': 'https://weibo.com/xianditie'
  },
  {
    'name': '重庆',
    'url': 'https://weibo.com/u/2152519810'
  },
  {
    'name': '成都',
    'url': 'https://weibo.com/cdmetroyy'
  },
  {
    'name': '武汉',
    'url': 'https://weibo.com/u/3186945861'
  },
  {
    'name': '南京',
    'url': 'https://weibo.com/u/2638276292'
  },
  # {
  #   'name': '深圳',
  #   'url': 'https://weibo.com/szmcservice'
  # }
]

def scrollBottom():
  jsscript = 'window.scrollTo(0, document.body.clientHeight)'
  driver.execute_script(jsscript)
  time.sleep(6)

def getTime(node, curYear, name):
  # year = time.localtime().tm_year
  # dateText = node.find('div', attrs={'class': 'WB_from S_txt2'}).find('a').string
  if name == '成都':
    temText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('】')[1]
    if temText.find('星期') != -1:
      mouthDayText = temText.split('（')[0].strip()
    else:
      mouthDayText = temText.split('日')[0].strip() + '日'
      # mouthDayText = temText.split('，')[0].strip()
    # mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('】')[1].split('，')[0].strip()

  elif name == '武汉':
    mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('】')[1].split('（')[0].strip()
  elif name == '西安':
    mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('，')[0].split('#客流数据#')[1].strip()
  elif name == '南京':
    mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('南京地铁')[1].split('日')[0].strip() + '日'
  elif name == '重庆':
    mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('，')[0].split('#')[2].strip()
  else:
    pass  
  # print(type(mouthDayText))
  # tup = dateText.partition('年')
  # print(tup)
  # if tup[0] != dateText:
  #   year = tup[0].replace('\n', '').replace('\r', '').strip()
  # return ustr
  temYear = ''
  if mouthDayText == '12月31日':
    temYear = int(curYear)-1
  else:
    temYear = curYear
  # print(str(year) + '年' + mouthDayText)
  if mouthDayText.find('年') != -1:
    return mouthDayText
  else:
    return str(temYear) + '年' + mouthDayText
  


def saveDataToDB(info):
  record_timestamp = int(time.mktime(time.strptime(info['date'], '%Y年%m月%d日')))
  # fetchOne if exist
  def save():
    sql = "insert into city_metro (city, date, passenger, timestamp) values ('%s', '%s', '%s', %d)" % (info['city'], info['date'], info['passenger'], record_timestamp)
    cur.execute(sql)
    db.commit()
  try:
    getOne = "select * from city_metro where city = '%s' and date = '%s'" % (info['city'], info['date'])
    cur.execute(getOne)
    res = cur.fetchone()
    print(res)
    if res == None:
      save()
    else:
      print('this record is existed')
  except:
    # no data insert record
    sql = "insert into city_metro (city, date, passenger, timestamp) values ('%s', '%s', '%s', %d)" % (info['city'], info['date'], info['passenger'], record_timestamp)
    cur.execute(sql)
    db.commit()
    pass
  # print(record_timestamp)
  

def getData(name, curYear):
  if name == '成都':
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    nodes = soup.find_all('div', attrs={'class': 'WB_detail'})
    if len(nodes) == 0:
      print('no data or empty page')
      return
    for item in nodes:
      nodeText = item.find('div', attrs={'class': 'WB_text W_f14'}).get_text()
      if nodeText.find('【客流播报】') != -1 or nodeText.find('【地铁客流】') != -1:
        temPassengerText = nodeText.split('万')[0]
        if temPassengerText.find('客运量') != -1: 
          passenger = temPassengerText.split('客运量')[1]
        elif temPassengerText.find('客运') != -1:
          passenger = temPassengerText.split('客运')[1]
        # passenger = nodeText.split('万')[0].split('客运量')[1]
        print(passenger)
        recordTime = getTime(item, curYear, name)
        print(recordTime)
        info = {
          'date': recordTime,
          'passenger': passenger,
          'city': name
        }
        saveDataToDB(info)
      else:
        print('no used item')
        pass
      pass
  elif name == '武汉':
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    nodes = soup.find_all('div', attrs={'class': 'WB_detail'})
    for item in nodes:
      nodeText = item.find('div', attrs={'class': 'WB_text W_f14'}).get_text()
      if nodeText.find('【昨日客流】') != -1:
        passenger = nodeText.split('万')[0].split('客运量（含换乘）为')[1]
        print(passenger)
        recordTime = getTime(item, curYear, name)
        print(recordTime)
        info = {
          'date': recordTime,
          'passenger': passenger,
          'city': name
        }
        saveDataToDB(info)
      else:
        print('no used item')
        pass
      pass
    pass
  elif name == '西安':
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    nodes = soup.find_all('div', attrs={'class': 'WB_detail'})
    for item in nodes:
      nodeText = item.find('div', attrs={'class': 'WB_text W_f14'}).get_text()
      if nodeText.find('#客流数据#') != -1:
        try:
          passenger = nodeText.split('万')[0].split('线网客流')[1]
        except Exception as e:
          if nodeText.find('达') != -1:
            passenger = nodeText.split('万')[0].split('达')[1]
          elif nodeText.find('线网客运量') != -1:
            passenger = nodeText.split('万')[0].split('线网客运量')[1]
          pass
        # passenger = nodeText.split('万')[0].split('线网客流')[1]
        print(passenger)
        recordTime = getTime(item, curYear, name)
        print(recordTime)
        info = {
          'date': recordTime,
          'passenger': passenger,
          'city': name
        }
        saveDataToDB(info)
      else:
        print('no used item')
        pass
      pass
    pass
  elif name == '南京':
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    nodes = soup.find_all('div', attrs={'class': 'WB_detail'})
    for item in nodes:
      nodeText = item.find('div', attrs={'class': 'WB_text W_f14'}).get_text()
      if nodeText.find('#昨日客流#') != -1:
        try:
          if nodeText.find('，') != -1:
            passenger = nodeText.split('，')[0].split('客运量')[1]
          elif nodeText.find(',') != -1:
            passenger = nodeText.split(',')[0].split('客运量')[1]
        except Exception as e:
          pass
        print(passenger)
        recordTime = getTime(item, curYear, name)
        print(recordTime)
        info = {
          'date': recordTime,
          'passenger': passenger,
          'city': name
        }
        saveDataToDB(info)
      else:
        print('no used item')
        pass
      pass
    pass
  elif name == '重庆':
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    nodes = soup.find_all('div', attrs={'class': 'WB_detail'})
    for item in nodes:
      nodeText = item.find('div', attrs={'class': 'WB_text W_f14'}).get_text()
      if nodeText.find('#昨日客运量#') != -1:
        passenger = nodeText.split('万')[0].split('线网客运量')[1]
        print(passenger)
        recordTime = getTime(item, curYear, name)
        print(recordTime)
        info = {
          'date': recordTime,
          'passenger': passenger,
          'city': name
        }
        saveDataToDB(info)
      else:
        print('no used item')
        pass
      pass
    pass
  else:
    pass


def spide():
  # loop to spider data
  for city in citys:
    url = city['url']
    driver.get(url)
    time.sleep(3)
    # scroll to bottom
    scrollTime = 4
    while scrollTime > 0:
      scrollBottom()
      scrollTime -= 1
      pass
    curYear = time.strftime('%Y', time.localtime())
    getData(city['name'], curYear)
    # temPage += 1
    # time.sleep(5)
    # while temPage <= pageCount:
    #   temPage = mainSpide(city, curYear, curMouth, str(temPage))
    #   pass
    pass


def job():
  spide()
  # print('do job')


scheduler = BackgroundScheduler()
scheduler.add_job(job, 'interval', minutes=10)
scheduler.start()

while True:
  pass