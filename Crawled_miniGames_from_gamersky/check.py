import pymongo

client = pymongo.MongoClient('localhost', 27017)
youxi = client['youxi']
mini = youxi['mini2']

# 筛选出所有大小小于 500M 的游戏
for a in mini.find({'大小':{'$lte':500}}):
    print(a)
