#coding=utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import pymysql

db = pymysql.connect(host='192.168.1.21', port=3306, user='root', passwd='123456', db='metro')

cur = db.cursor()

driver = webdriver.Chrome()
driver.set_window_size(1200, 800)

def login():
  # do login weibo
  driver.get('https://weibo.com/')
  time.sleep(10)
  driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[1]/div/a[2]').click()
  # scan qrcode to login in 30 s
  time.sleep(20)
  pass

login()

citys = [
  {
    'name': '重庆',
    'url': 'https://weibo.com/u/2152519810?is_all=1&'
  },
  {
    'name': '成都',
    'url': 'https://weibo.com/cdmetroyy?is_all=1&'
  },
  {
    'name': '武汉',
    'url': 'https://weibo.com/u/3186945861?is_all=1&'
  },
  {
    'name': '西安',
    'url': 'https://weibo.com/xianditie?is_all=1&'
  },
  {
    'name': '南京',
    'url': 'https://weibo.com/u/2638276292?is_all=1&s'
  },
  # {
  #   'name': '深圳',
  #   'url': 'https://weibo.com/szmcservice?is_all=1&'
  # }
]

years = ['2019']
# mouths = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
mouths = ['01', '02']

def scrollBottom():
  jsscript = 'window.scrollTo(0, 10000)'
  driver.execute_script(jsscript)
  time.sleep(5)

def getPageSize():
  try:
    totalEl = driver.find_element_by_css_selector('.W_pages > .list > .S_txt1')
    print(totalEl.get_attribute('action-data').split('&')[1])
    return int(totalEl.get_attribute('action-data').split('&')[1].split('=')[1])
  except Exception as e:
    print('no such el reason only 1 page')
    return 1
  

def getTime(node, curYear, name):
  # year = time.localtime().tm_year
  # dateText = node.find('div', attrs={'class': 'WB_from S_txt2'}).find('a').string
  if name == '成都':
    mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('】')[1].split('，')[0].strip()
  elif name == '武汉':
    mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('】')[1].split('（')[0].strip()
  elif name == '西安':
    mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split(';')[1].split('，')[0].strip()
  elif name == '南京':
    mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('南京地铁')[1].split('客运量')[0].strip()
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
  # if mouthDayText == '1月1日':
  #   year = int(year)-1
  # print(str(year) + '年' + mouthDayText)
  return str(curYear) + '年' + mouthDayText


def saveDataToDB(info):
  record_timestamp = int(time.mktime(time.strptime(info['date'], '%Y年%m月%d日')))
  # print(record_timestamp)
  sql = "insert into city_metro (city, date, passenger, timestamp) values ('%s', '%s', '%s', %d)" % (info['city'], info['date'], info['passenger'], record_timestamp)
  cur.execute(sql)
  db.commit()

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
        passenger = nodeText.split('万')[0].split('客运量')[1]
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
        passenger = nodeText.split('万')[0].split('线网客流')[1]
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
        passenger = nodeText.split('，')[0].split('客运量')[1]
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


def mainSpide(city, curYear, curMouth, curPage):
  url = city['url'] + 'stat_date=' + curYear + curMouth + '&page=' + curPage + '#feedtop'
  driver.get(url)
  time.sleep(3)
  # scroll to bottom
  scrollTime = 4
  while scrollTime > 0:
    scrollBottom()
    scrollTime -= 1
    pass
  getData(city['name'], curYear)
  nextPage = int(curPage) + 1
  time.sleep(5)
  return nextPage

# loop to spider data
for city in citys:
  for curYear in years:
    for curMouth in mouths:
      temPage = 1
      initPage = '1'
      url = city['url'] + 'stat_date=' + curYear + curMouth + '&page=' + initPage + '#feedtop'
      driver.get(url)
      time.sleep(3)
      # scroll to bottom
      scrollTime = 4
      while scrollTime > 0:
        scrollBottom()
        scrollTime -= 1
        pass
      pageCount = getPageSize()
      # get page size
      getData(city['name'], curYear)
      temPage += 1
      time.sleep(5)
      while temPage <= pageCount:
        temPage = mainSpide(city, curYear, curMouth, str(temPage))
        pass
      pass
    pass
  


