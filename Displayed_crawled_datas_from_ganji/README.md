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
