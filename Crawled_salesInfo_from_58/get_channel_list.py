from bs4 import BeautifulSoup
import requests, pymongo, re

client = pymongo.MongoClient('localhost', 27017)
wuba = client['wuba_sale']
channel_list = wuba['channel_list']  # 存放频道信息

# 起始地址
start_url = 'http://bj.58.com/sale.shtml'
url_host = 'http://bj.58.com'


# 获取频道地址
def get_index_url(url):
	# url = start_url
	wb_data = requests.get(url)
	soup = BeautifulSoup(wb_data.text, 'lxml')
	links = soup.select('ul.ym-submnu > li > b > a')  # 获取所有频道入口地址
	channel_list = []
	for link in links:
		page_url = url_host + link.get('href')
		if 'shoujihao' in page_url:
			pass
		else:
			print(page_url)
			channel_list.append(page_url)  # 存入collection


get_index_url(start_url)
