#coding=utf-8
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os

# print(os.cpu_count)
# print(selenium)
# print(webdriver)

baseUrl = 'https://s.weibo.com/weibo?q=%23%E6%98%A8%E6%97%A5%E5%AE%A2%E8%BF%90%E9%87%8F%23&from=default&page='
driver = webdriver.Chrome()

pageNum = 1

# print(baseUrl + pageNum)

def deepSpide():
  global pageNum
  driver.get(baseUrl + str(pageNum))
  html = driver.page_source
  # html = driver.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[1]')
  soup = BeautifulSoup(html, 'lxml')
  # soup.encode('utf-8')
  nodes = soup.find_all('div', attrs={'class': 'card-feed'})
  # nodes.encode('utf-8')
  print(len(nodes))
  for item in nodes:
    # print(item.prettify())
    # dateText = item.find('p', attrs={'class': 'form'})
    # ustr = dateText.find('a').string
    # print(dateText.contents)
    # content = item.find('div', attrs={'class': 'content'})
    # print(content)
    pass
  # print(soup.encode('gbk'))


def getTime():
  print('time')

deepSpide()
driver.quit()