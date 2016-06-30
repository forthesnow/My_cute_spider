##山寨赶集二手网

  这是个用Django框架做的一个小网站，数据来自之前从赶集网爬取来的数据。
  如果具备python环境，可以直接在manage.py所在目录下输入：
  
  `python manage.py runserver`
  
  之后会进入商品信息页面：
  
  ![index_data.html](https://github.com/forthesnow/My_python_path/blob/master/Displayed_crawled_datas_from_ganji/django_ganji_data.png)
  
  点击标题会直接跳转到这个商品在赶集网的链接
  
  左侧黑栏的前两个选项分别对应 index_data.html 和 chart2.html 这两个页面
  
  点击"Charts"即可进入商品数据分析页面：
  
  ![chart2.html](https://github.com/forthesnow/My_python_path/blob/master/Displayed_crawled_datas_from_ganji/django_ganji_charts.png)
  
  
* models.py

将之前存入赶集网爬取信息的数据库映射到models中封装成一个ItemInfo类，类中所有对象对应每个商品信息

```
from mongoengine import *
from mongoengine import connect
connect('ganji', host='127.0.0.1', port=27017)

# ORM

class ItemInfo(Document):
    area = ListField(StringField())
    title = StringField()
    saled = StringField()
    cates = ListField(StringField())
    price = StringField()
    pub_date = StringField()
    url = StringField()
    newist = StringField()
    img = StringField()
    type = StringField()

    meta = {'collection':'item_info2'}   #使用 ganji - item_info2 这个collection中的数据
```

* url.py

本次一共提供两个页面，当请求/index/时，调用index函数，将渲染好的index_data.html返还；当请求/chart/时，调用chart函数，将渲染好的chart2.html返还。而这两个页面都披着new_base.html这层皮

```
from django.conf.urls import url
from django.contrib import admin
from django_web.views import index,chart

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', index),   # 数据页面响应
    url(r'^chart/', chart)    # 图表页面响应
]
```
* views.py

views的前一部分主要是先生成chart2.html显示图表所需的数据，也可以说是洗一下数据。后一部分主要是定义如何将这些数据按页展示，修改limit的值就可以设置每页显示的商品数量。

```
from django.shortcuts import render
from django_web.models import ItemInfo
from django.core.paginator import Paginator

#============================================== <<<< DATA GENS >>>> ====================================================

#  区域内单类目发帖量前三名
def topx(date1,date2,area,limit):

    pipeline = [
        {'$match':{'$and':[{'pub_date':{'$gte':date1,'$lte':date2}},{'area':{'$all':area}}]}}, # 发帖日期区间*地区
        {'$group':{'_id':{'$slice':['$cates',0,1]},'counts':{'$sum':1}}}, # 以商品的类名进行分组 并计总量
        {'$limit':limit}, # 前几名
        {'$sort':{'counts':-1}} # 倒序排列
    ]

    for i in ItemInfo._get_collection().aggregate(pipeline):
        data = {
            'name': i['_id'][0], # 类目名
            'data': [i['counts']], # 发帖量
            'type': 'column' # 柱状
        }
        yield data  # 迭代生成数据
# 想要生成的三组数据已经弄好了，之后赋给highcharts就行了
series_CY = [i for i in topx('2016.06.12','2016.06.26',['朝阳'],3)]
series_TZ = [i for i in topx('2016.06.12','2016.06.26',['通州'],3)]
series_HD = [i for i in topx('2016.06.12','2016.06.26',['海淀'],3)]


# #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# 筛选单类目发帖总量前6名
def total_post():
    # 条件
    pipeline = [
        {'$group':{'_id':{'$slice':['$cates',0,1]},'counts':{'$sum':1}}},
        {'$sort': {'counts': -1}}, # 倒序
        {'$limit':6}
    ]

    for i in ItemInfo._get_collection().aggregate(pipeline):
        print(i)
        data = {
            'name':i['_id'][0], # 类名
            'y':i['counts'] # 数量
        }
        yield data

# 发帖量最高的6个类目
series_post = [i for i in total_post()]


# #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 成交用时为1天的类目分布（前7名）
def one_day_deal_cate():
    pipeline = [
        {'$match':{'$and':[{'pub_date':{'$gte':'2016.06.12','$lte':'2016.06.26'}},{'saled':'1'}]}},
        {'$group':{'_id':{'$slice':['$cates',0,1]},'counts':{'$sum':1}}},
        {'$sort':{'counts':1}},
        {'$limit':7}
    ]

    for i in ItemInfo._get_collection().aggregate(pipeline):
        data = {
            'name':i['_id'][0],
            'y':i['counts']
        }
        yield data
# 成交用时为1天的地区分布（前7名）
def one_day_deal_area():
    pipeline = [
        {'$match':{'$and':[{'pub_date':{'$gte':'2016.06.25','$lte':'2016.06.26'}},{'saled':'1'}]}},
        {'$group':{'_id':{'$slice':['$area',1,1]},'counts':{'$sum':1}}},
        {'$sort':{'counts':1}},
        {'$limit': 7}
    ]

    for i in ItemInfo._get_collection().aggregate(pipeline):
        data = {
            'name':i['_id'][0],
            'y':i['counts']
        }
        yield data

pie1_data = [i for i in one_day_deal_cate()]
pie2_data = [i for i in one_day_deal_area()]




#============================================== <<<< PAGE VIEWS >>>> ===================================================


def index(request):
    limit = 15 # 一页十五个
    arti_info = ItemInfo.objects # model层定义好的数据库对象
    paginatior = Paginator(arti_info,limit)  # 创建分页
    page = request.GET.get('page',1) # 取'page'的GET参数，如果没有取到，默认为1
    loaded = paginatior.page(page)  # page 1 of ***

    context = {
        'ItemInfo':loaded,
        'counts':arti_info.count(),
        'last_time':arti_info.order_by('-pub_date').limit(1),
    }

    return render(request,'index_data.html',context)

def chart(request):
    context = {
        # 都是上面已经得到的数据
        'chart_CY':series_CY,
        'chart_TZ':series_TZ,
        'chart_HD':series_HD,
        'series_post':series_post,
        'pie1_data':pie1_data,
        'pie2_data':pie2_data
    }
    return render(request,'chart2.html',context)
```

