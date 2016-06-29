from multiprocessing import Pool
from get_item_info import get_item_url,get_item_info
from get_channel_list import channel_list
import pymongo

client = pymongo.MongoClient ('localhost', 27017)
wuba = client['wuba_sale']
url_list = wuba['url_list']

if __name__ == '__main__':
    pool = Pool(processes=4)
    # pool = Pool(processes=6)
    # 生成每个频道前五页的商品链接表
    for channel in channel_list:
         for i in range(1,5):
             get_item_url(channel,i)
    # 从数据库中取出商品链接
    urls = [url['url'] for url in url_list.find()]
    # 去重之后就可以开始爬取了
    pool.map(get_item_info,set(urls))
