#coding=utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import pymysql

db = pymysql.connect(host='39.108.210.247', user='root', passwd='lzr5680545', db='metro', port=3306)

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
  # {
  #   'name': '西安',
  #   'url': 'https://weibo.com/xianditie?is_all=1&'
  # },
  {
    'name': '重庆',
    'url': 'https://weibo.com/u/2152519810?is_all=1&'
  },
  # {
  #   'name': '成都',
  #   'url': 'https://weibo.com/cdmetroyy?is_all=1&'
  # },
  {
    'name': '武汉',
    'url': 'https://weibo.com/u/3186945861?is_all=1&'
  },
  # {
  #   'name': '南京',
  #   'url': 'https://weibo.com/u/2638276292?is_all=1&s'
  # },
  # {
  #   'name': '深圳',
  #   'url': 'https://weibo.com/szmcservice?is_all=1&'
  # }
]

years = ['2020']
mouths = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
# mouths = ['03']

def scrollBottom():
  jsscript = 'window.scrollTo(0, document.body.clientHeight)'
  driver.execute_script(jsscript)
  time.sleep(6)

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
  temDate = node.find('div', attrs={'class': 'WB_from S_txt2'}).get_text().strip()
  publishYear = ''
  if temDate.find('-') != -1:
    publishYear = temDate.split('-')[0].strip()
    pass
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
    # mouthDayText = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('南京地铁')[1].split('日')[0].strip() + '日'
    tem = node.find('div', attrs={'class': 'WB_text W_f14'}).get_text().split('南京地铁')[1].split('，')[0].strip()
    if tem.find('日') != -1:
      mouthDayText = tem.split('日')[0].strip() + '日'
    elif tem.find('客运量') != -1:
      mouthDayText = tem.split('客运量')[0].strip() + '日'
    elif tem.find('线网') != -1:
      mouthDayText = tem.split('线网')[0].strip() + '日'
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
  # curYear = publishYear ? publishYear : curYear
  if publishYear != '':
    curYear = publishYear
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
        # print('no used item')
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
        # print('no used item')
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
        # print('no used item')
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
        if passenger.find('万') != -1:
          passenger = passenger.split('万')[0]
        if passenger.find(', ') != -1:
          passenger = passenger.split(',')[0]
        if passenger.find('其中') != -1:
          passenger = passenger.split('其中')[0]
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
        # print('no used item')
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
        # print('no used item')
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
  


