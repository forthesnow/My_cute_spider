from bs4 import BeautifulSoup
import requests,pymongo

#创建mongo数据表
client = pymongo.MongoClient('localhost',27017)
xiaozhu = client['xiaozhu']
links = xiaozhu['links']
rent_info = xiaozhu['rent_info']
# 这个网站只有300个租房信息，也是醉了

# 爬取一间房的详细信息，返回一个字典

def yijianfang(url):
	# 解析网页结构
	wb_data = requests.get(url)
	soup = BeautifulSoup(wb_data.text, 'lxml')
	# 获取标题
	titlet = soup.select('div.pho_info > h4 > em')
	title = titlet[0].get_text()
	# 获取房源地址
	addrs = soup.select('div.pho_info > p > span.pr5')
	addr = addrs[0].get_text().strip() if soup.select('div.pho_info > p > span.pr5') else None
	# 获取日租金
	pays = soup.select('div.day_l > span')
	pay = '￥ ' + pays[0].get_text()
	# 获取房源照片
	imgs = soup.select('img#curBigImage')
	img = imgs[0].get('src')
	# 获取房东照片
	owners = soup.select('div.member_pic > a > img')
	owner = owners[0].get('src')
	# 获取房东艺名
	owner_names = soup.select('div.w_240 > h6 > a.lorder_name')
	owner_name = owner_names[0].get_text()
	# 获取房东性别（不一定有）
	owner_sexs = soup.select('div.w_240 > h6 > span')
	owner_sex = ''
	if 'boy' in str(owner_sexs[0]):
		owner_sex = '男'
	elif 'girl' in str(owner_sexs[0]):
		owner_sex = '女'
	else:
		owner_sex = '无性'

	data = {
		'房间标题': title,
		'所在地址': addr,
		'日·租金': pay,
		'图片地址': img,
		'房东长相地址': owner,
		'房东艺名': owner_name,
		'房东的性': owner_sex
	}
	return data

# 一共要爬取14页的租房信息
urls = ['http://bj.xiaozhu.com/search-duanzufang-p{}-0/'.format(str(i)) for i in range(1, 14, 1)]
# 判断是否已经获取过url信息，如果已经抓过了就跳过
if links.find().count():
	pass
else:
	# 获取每个房源的链接url，存入到 links 这个collection中
	for url in urls:  # 爬取一页租房信息 一页24个
		page = requests.get(url)
		soup = BeautifulSoup(page.text, 'lxml')
		urls = soup.select('li > div.result_btm_con.lodgeunitname')
		for url in urls:
			link = url.get('detailurl')   # 获取每个房的具体信息链接（干货）
			print(link)     #只是为了让你知道程序还活着
			links.insert_one({'url':link})  #放入collection中

for i in links.find():
	print(i['title']) # 怕你无聊
	a = yijianfang(i['url'])  
	rent_info.insert_one(a)    #放进collection
