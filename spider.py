import requests

url = 'https://www.chengdurail.com/index.html'

res = requests.get(url)
# res.encoding = 'utf-8'
# res.text.encode('GBK', 'ignore')

print(res.text.encode('GB18030', 'ignore'))