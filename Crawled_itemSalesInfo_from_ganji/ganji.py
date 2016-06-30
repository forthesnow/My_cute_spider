from bs4 import BeautifulSoup
from multiprocessing import Pool
import requests,pymongo,time


start_url = 'http://bj.ganji.com/wu/'
url_host = 'http://bj.ganji.com'

# 创建数据库

client = pymongo.MongoClient('localhost', 27017)
ganji = client['ganji2']
channel_list = ganji['channel_list']  # 频道列表
url_list = ganji['url_list']  #  商品地址链接列表
item_info = ganji['item_info']  #  商品详细信息
url_suc = ganji['url_suc']  #  已成功爬取的商品
url_fal = ganji['url_fal']  #  失败的商品


def get_index_url(url):   #生成频道链接列表
    wb_data = requests.get(url)
    wb_data.encoding = 'UA-479320-1' # 不改的话，有一小部分解码会出现问题
    soup = BeautifulSoup(wb_data.text, 'lxml')
    links = soup.select('dl > dt > a')
    for link in links:
        href = url_host+link.get('href')
        channel_list.insert_one({'channel':href})

# 判断数据库中是否有频道信息，如果有就跳过，如果没有就调用频道生成函数
if channel_list.find().count() :  
    pass
else:
    get_index_url(start_url)
# 用来生成商品信息链接
def get_item_url(channel,page):  
    time.sleep(1)
    urls = '{}o{}'.format(channel, str(page))
    try:
        wb_data = requests.get(urls)
        soup = BeautifulSoup(wb_data.text, 'lxml')
        if soup.select('a.ft-tit'):     #选中每个商品的url所在标签
            urlsun = soup.select('a.ft-tit')
            for urlun in urlsun:
                url = urlun.get('href')
                if 'zhuanzhuan' in url:   
                    pass
                else:
                    url_list.insert_one({'url':url})  # 把每个商品链接加入到url_list中
                    print(url)
    except Exception as e:
        print(e)
        url_fal.insert_one({'url':urls})

def get_item_info(url):    #爬取每个商品，需要传入商品页面链接
    try:
        url_suc.insert_one({'url':url})
        wb_data = requests.get(url)
        soup = BeautifulSoup(wb_data.text, 'lxml')
        # 下面是商品信息的抓取
        title = soup.select('h1.title-name')[0].get_text() if soup.select('h1') else None  # 标题
        date = soup.select('i.pr-5')[0].get_text().split()[0:2] if soup.select('i.pr-5') else 0  #  日期
        saled = ''  #  假的，模仿物品从发帖到交易成功的天数，只有一少部分商品会有这个属性
        try:
            sales = date[-1][-2:-1]
            if sales == '4':
                saled = date[-1][1]
        except:
            pass
        type = soup.select('ul.det-infor > li > span > a')[0].get_text() if soup.select(
            'ul.det-infor > li > span > a') else None  #  商品所属分类
        price = soup.select('i.f22.fc-orange.f-type')[0].get_text()  #  商品价格
        place = []  #  商品所在区域
        if soup.select('ul.det-infor > li:nth-of-type(3) > a'):
            places = soup.select('ul.det-infor > li:nth-of-type(3) > a')
            for a in places:
                place.append(a.text)
        newist = ''  #  商品新旧程度  很多商品都没有这个属性
        if soup.select('ul.second-det-infor.clearfix > li '):
            news = soup.select('ul.second-det-infor.clearfix > li ')
            for new in news:
                if '新' in new.text:
                    newist = new.text[5:].strip()
        img = ''  #  商品图片链接，暂时先只获取一个
        if soup.select(
                '#wrapper > div.content.clearfix > div.leftBox > div:nth-of-type(5) > div > a:nth-of-type(1) > img'):
            img = soup.select(
                '#wrapper > div.content.clearfix > div.leftBox > div:nth-of-type(5) > div > a:nth-of-type(1) > img')[
                0].get('src')
        cates = []  #  这个也是商品分类
        if soup.select('body > div.h-search > div > div.h-crumbs > div > a'):
            catess = soup.select('body > div.h-search > div > div.h-crumbs > div > a')[2:]
            for cate in catess:
                cates.append(cate.text)
        data = {
            'url': url,
            'title': title,
            'pub_date': date,
            'saled': saled,
            'type': type,
            'price': price,
            'area': place,
            'newist': newist,
            'img': img,
            'cates': cates

        }
        item_info.insert_one(data)  # 每个商品的详细信息都存入 item_info中
        print('Done!')
        time.sleep(1)  
    except Exception as e:
        print(e)
        url_fal.insert_one({'url': url})  # 失败了就存一下
	    
def get_all_links(channel): # 这个函数决定了爬取每个频道的前多少页
    for i in range(1,13):
        get_item_url(channel,i)


TOTALURL = 0  # 商品链接地址总数
if __name__ == '__main__':
    pool = Pool(processes=4)
    list = [u['channel'] for u in channel_list.find()]  # 取出所有的频道
    TOTALURL = url_list.find().count()
    if TOTALURL:   #检查目标链接列表是否为空，如果有了，就直接爬取商品，如果没有就扫商品链接
        pass
    else:
        pool.map(get_all_links, list)
        TOTALURL = url_list.find().count()
    print(TOTALURL)
    target = [z['url'] for z in url_list.find()]  # 目标链接地址列表
    done = [i['url'] for i in item_info.find()]   # 已完成地址列表
    a = set(target) # 去重
    b = set(done)
    c = a - b  # 还没有爬取的地址列表
    print(len(c))
    pool.map(get_item_info,c)  # 开搞
