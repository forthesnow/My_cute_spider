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




