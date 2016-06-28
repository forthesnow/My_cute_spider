from bs4 import BeautifulSoup
import requests, urllib.request, time

# 先按规律生成煎蛋网前五页的网址
urls = ['http://jiandan.net/page/{}'.format(str(i)) for i in range(1, 5)]


def single(url):
	# 这次解析煎蛋网是要加上header的，已开防爬，机器人什么都爬不到
	header = {
		'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.154 Safari/537.36 LBBROWSER'}
	# 解析网页
	wb_data = requests.get(url, headers=header)
	soup = BeautifulSoup(wb_data.text, 'lxml')
	# 定义图片存放位置
	folder_path = 'E:\\python\jiandan2\\'
	# 获取图片列表（未清洗）
	imgs = soup.select('div.thumbs_b > a > img.lazy')
	imglist = []
	for img in imgs:
		a = img.get('data-original')
		imglist.append(a.replace('//', 'http://'))
	#通过urllib库提供的方法把图片下载下来
	for img in imglist:
		urllib.request.urlretrieve(img, folder_path + img[-8:])    
		print('Done')
		time.sleep(0.5)   #睡一会，别累疯(封)了


for url in urls:
	single(url)
