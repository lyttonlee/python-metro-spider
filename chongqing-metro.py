#coding=utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import pymysql

db = pymysql.connect(host='192.168.1.21', port=3306, user='root', passwd='123456', db='metro')

cur = db.cursor()

# print(os.cpu_count)
# print(selenium)
# print(webdriver)

baseUrl = 'https://s.weibo.com/weibo?q=%23%E6%98%A8%E6%97%A5%E5%AE%A2%E8%BF%90%E9%87%8F%23&from=default&page='
driver = webdriver.Chrome()

pageNum = 1

# print(baseUrl + pageNum)

def login_weibo():
  print('login')
  driver.find_element_by_xpath('//*[@id="weibo_top_public"]/div/div/div[3]/div[2]/ul/li[3]/a').click()
  # time.sleep(1)
  # driver.find_element_by_xpath('//*[@id="layer_16106933244091"]/div[2]/div[3]/div[1]/a[2]').click()
  time.sleep(30)
  pass

def deepSpide():
  global pageNum
  if pageNum > 32:
    return
  driver.get(baseUrl + str(pageNum))
  # driver.switch_to.window()
  if pageNum == 1:
    time.sleep(3)
    login_weibo()
  html = driver.page_source
  # html = driver.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[1]')
  soup = BeautifulSoup(html, 'lxml')
  # soup.encode('utf-8')
  nodes = soup.find_all('div', attrs={'class': 'card-feed'})
  # nodes.encode('utf-8')
  print(len(nodes))
  for item in nodes:
    # print(item.prettify())
    info = getTime(item)
    if info == 'not record':
      pass
    else:
      saveDataToDB(info)
      pass
    pass
  pageNum += 1
  time.sleep(3)
  deepSpide()


def getTime(node):
  year = time.localtime().tm_year
  tempassenger = node.find('p', attrs={'class': 'txt'}).get_text()
  if len(tempassenger.split('交通线网客运量')) == 1:
    return 'not record'
  passenger = tempassenger.split('交通线网客运量')[1].split('万')[0]
  dateText = node.find('p', attrs={'class': 'from'}).find('a').get_text()
  mouthDayText = node.find('p', attrs={'class': 'txt'}).find('a').next_sibling.string.split('，')[0].replace('\n', '').replace('\n', '').strip()
  # print(type(mouthDayText))
  # print(mouthDayText)
  print(passenger)
  tup = dateText.partition('年')
  # print(tup)
  if tup[0] != dateText:
    year = tup[0].replace('\n', '').replace('\n', '').strip()
  # return ustr
  print(str(year) + '年' + mouthDayText)
  return {
    'city': '重庆',
    'date': str(year) + '年' + mouthDayText,
    'passenger': passenger
  }


def saveDataToDB(info):
  record_timestamp = int(time.mktime(time.strptime(info['date'], '%Y年%m月%d日')))
  print(record_timestamp)
  sql = "insert into city_metro (city, date, passenger, timestamp) values ('%s', '%s', '%s', %d)" % (info['city'], info['date'], info['passenger'], record_timestamp)
  cur.execute(sql)
  db.commit()



deepSpide()
cur.close()
db.close()
driver.quit()
