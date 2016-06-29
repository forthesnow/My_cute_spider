from bs4 import BeautifulSoup
import requests,pymongo

# 之前经常在游民下游戏，现在没有台式机了，只能玩玩比较小的游戏了，这次就爬一爬游民的500来M的游戏

# 创建数据库空间
client = pymongo.MongoClient('localhost', 27017)
youxi = client['youxi']
mini = youxi['mini2']

# 游民的网页简直了，复制了再贴上去都是不好使的，所幸在切换页面时监听到了特征字段稍作修改就可以得到网页的规律

# 地址列表  前面的都是40 50G 的游戏  爬了也白爬
urls = ['http://down.gamersky.com/page/pc/0-0-0-0-0-0-0-40_{}.html'.format(str(i)) for i in range (251,800)]

for url in urls:
    try:
        # 解析网页
        wb_data = requests.get(url)
        soup = BeautifulSoup(wb_data.text,'lxml')
        # 获取游戏信息
        titles = soup.select('div.tit > a')
        downs = soup.select('a.download')
        sizes = soup.select('body > div > ul > li > div:nth-of-type(7)')
        dates = soup.select('body > div > ul > li > div:nth-of-type(3)')
        types = soup.select('body > div > ul > li > div:nth-of-type(4)')
        langs = soup.select('body > div > ul > li > div:nth-of-type(5)')
        # 一个页面有多个游戏  所以不能像原来那样一个页面爬取一个
        for title,date,type,lang,size,down in zip(titles,dates,types,langs,sizes,downs):
            # 如果大小是论G的，那就乘以1000
            if size.get_text().split('：')[1][-2] == 'G':
                #print(size.get_text().split('：')[1])
                big =float(size.get_text().split('：')[1][:-2])*1000
            # 否则肯定就是按M算的
            else:
                big = float(size.get_text().split('：')[1][:-2])
                #print(size.get_text().split('：')[1])
            data={
                '题目': title.get_text(),
                #'日期': date.get_text().split('：')[1],
                '大小': big,# + 'MB',
                '地址': down.get('href'),
                #'类型': type.get_text().split('：')[1],
            }
            print(data)
            mini.insert_one(data)
    except Exception as e:
        print(e)


