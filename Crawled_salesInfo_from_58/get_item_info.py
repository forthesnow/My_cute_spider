from bs4 import BeautifulSoup
import requests, pymongo, time

client = pymongo.MongoClient ('localhost', 27017)
wuba = client['wuba_sale']
url_list = wuba['url_list']
item_info = wuba['item_info']

url_suc = wuba['url_suc']
url_fal = wuba['url_fal']
page_parse_fal = wuba['page_parse_fal']

# 这是一个获取商品链接的函数
def get_item_url(channel, page):
	# 按规律生成频道-页面地址，是商品链接的上一级
	url = '{}pn{}'.format (channel, str (page))
	try:
		# 解析网页
		wb_data = requests.get (url)
		soup = BeautifulSoup (wb_data.text, 'lxml')
		# 选中包含商品链接的a标签
		if soup.select ('td.t > a.t'):
			urlsun = soup.select ('td.t > a.t')
			for urlun in urlsun:
				url = urlun.get ('href')
				if 'zhuanzhuan' in url:
					pass
				else:
					url_list.insert_one ({'url': url})  # 目标地址
					print(url)
	# 如果失败了就记录下来
	except Exception as e:
		page_parse_fal.insert_one(url)
		print(e)
#  这是一个获取商品详细信息的函数
def get_item_info(url):
	try:
		#解析网页
		wb_data = requests.get (url)
		url_suc.insert_one ({'url': url})
		soup = BeautifulSoup (wb_data.text, 'lxml')
		# 获取标题
		title = soup.select ('h1')[0].get_text () if soup.select ('h1') else None
		# 获取价格
		price = soup.select ('span.price.c_f50')[0].get_text ().split ()[0] if soup.select (
			'span.price.c_f50') else None
		# 获取发帖日期
		date = soup.select ('li.time')[0].get_text () if soup.select ('li.time') else None
		# 获取区域   不同的频道  网页结构可能不同  所以有两种方式获取区域
		areaa = []
		if soup.select ('span.c_25d > a'):
			areas = soup.select ('li > div.su_con > span.c_25d > a')
		else:
			areas = soup.select('div.su_con > a')
		for i in areas:
			if i.get ('target'):
				pass
			else:
				areaa.append (i.get_text ())
		print (url)
		#  获取电话号码
		tele = ''
		if soup.select ('#t_phone'):
			tels = soup.select ('span#t_phone')
			for tel in tels:
				if len (tel.get_text ()) > 7:
					tele = tel.get_text ().split ()[0]
				else:
					pass
		#  得到的信息存到data中，然后将每个data保存到item_info中
		data = {
			'标题': title,
			'价格': price,
			'日期': date,
			'区域': areaa,
			'电话': tele,
			'url': url
		}
		item_info.insert_one (data)
		time.sleep (1)
		print(data)
	except Exception as e:
		print (e)
		url_fal.insert_one ({'url': url})

