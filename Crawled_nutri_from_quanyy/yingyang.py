from bs4 import BeautifulSoup
import requests
import pymongo

# 创建数据库
client = pymongo.MongoClient('localhost', 27017)
yingyang = client['yingyang']
nutri_cn = yingyang['nutri_cn']
fal_url = yingyang['fal_url']
nutri_en = yingyang['nutri_en']

# 网页规律还是很容易发现的
urls = ['http://www.quanyy.com/?Tools/tools_cf_info/aid/1/bid/13/id/{}.html'.format(i) for i in range(11, 1716)]
for i in urls:
    try:
        wb_data = requests.get(i)
        soup = BeautifulSoup(wb_data.text, 'lxml')
        # 网页信息都是放到td中的，特征不明显，纯按排列顺序区分的  可以将所有td装到一个列表中，按序号进行区分
        tds = soup.select('tbody > tr > td ')
        count = 0
        nut = {} #
        while count <= 76:  # 一页共76个td
            if tds[count].get('id'):  # 网页中装营养名称的td没有id  可能是因为这种食物不含这样的营养  而所有有值的td都有一个id
                name = tds[count - 1].text  # 有ID的td装着值  它前一个td装着它的名称
                try:
                    value = float(tds[count].text)   #  如果有值   它就可以被转成浮点数  如果没有  就会失败
                except:
                    if tds[count].get('id') != 'fd_name' and tds[count].get('id') != 'sub_category':   #  跳过食物名称和所属分类  剩下的就都是营养成分了  如果营养成分的值不能转成浮点数  那就是没有值  是一些转义字符
                        value = 0
                    else:
                        value = tds[count].text   # 食物名称和食物分类这两td就用他们本来的字符串好了
                nut.update({name: value}) # 将每种成分按照‘名称：数值’的形式存入数据库
            count += 1
        nutri_cn.insert(nut)
        print(nut['食物名称：'])

    except Exception as b:  #万一出错了  输出一下错误原因
        print(b)
