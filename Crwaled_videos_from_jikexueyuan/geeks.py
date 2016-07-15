from bs4 import BeautifulSoup
import requests, urllib.request, time, pymongo, os

client = pymongo.MongoClient ('localhost', 27017)
geeks = client['geeks2']    #爸爸
outer = geeks['outer']      #装一个课程的地址链接  如：#http://www.jikexueyuan.com/course/254.html
inner = geeks['inner']      #装一节课of一个课程的地址链接  如：#http://www.jikexueyuan.com/course/254_3.html
video = geeks['video']      #装视频链接源地址
video_done = geeks['video_done']
video_fal = geeks['video_fal']
inner_fal = geeks['inner_fal']

folder_base = 'E:\\python\Geek\\'   #存视频的目录
course_index = 'http://www.jikexueyuan.com/course/'
course_inter = ['http://www.jikexueyuan.com/course/?pageNum={}'.format(i) for i in range(1,97)]  #本想用判断做的，谁知这么容易就能获得

# 获取课程链接
def get_course_pages(url):
    wb_data = requests.get (url)
    soup = BeautifulSoup (wb_data.text, 'lxml')
    links = soup.select ('h2.lesson-info-h2 > a')
    for link in links:
        data = {
            'name': link.text,
            'url': link.get ('href')
        }
        outer.insert (data) #http://www.jikexueyuan.com/course/254.html
        print(data)
        time.sleep(1)
        
# 获取课节链接
def get_lesson_pages(url):
    try:
        wb_data = requests.get (url)
        soup = BeautifulSoup (wb_data.text, 'lxml')
        courses = soup.select ('div.text-box')
        course_names = soup.select ('div.text-box > h2 > a')
        num = len (courses)
        video_from = url[:-5] + '_' + '{}' + '.html'
        video_froms = [video_from.format (i) for i in range (1, num + 1)]
        for n, v in zip (course_names, video_froms):
            data = {
                'name': n.text,
                'video_from': v
            }
            inner.insert(data)  #http://www.jikexueyuan.com/course/254_3.html
            print (data)
            time.sleep (1)
    except:
        print('parse inner_page failed')
        
# 获取视频源地址
def get_video_srcs(url):
    try:
        header = {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.154 Safari/537.36 LBBROWSER',
            'Cookie': 'gr_user_id=36798f8e-978a-4083-a82c-db40c016946a; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22155aa73aede7dc-01252bdee-3069435a-100200-155aa73aedf642%22%7D; stat_uuid=1467443580944763170814; sso_closebindpop=bindphone; looyu_id=1b82690c9c54bfc8c26dd28198d10a5a9b_20001269%3A3; _99_mon=%5B0%2C0%2C0%5D; _gat=1; ohterlogin=qq; uname=qq_92je0muq; uid=5228427; code=702ZEP; authcode=020dQSkYh%2BkNzTNmO%2FzrAHypDpXsx%2BUcWwth9QstfB4HOA5fx%2FEg%2F%2BP88vbQqXWK6ln1Z7j1ljDgUF%2Ffef9mi%2Bxc0pOMlmbdctXsD4C376LZoAFQctnNW88Vd8lfL24; level_id=3; is_expire=0; domain=9709704047; stat_fromWebUrl=; stat_ssid=1467721369114; Hm_lvt_f3c68d41bda15331608595c98e9c3915=1467443555,1467488139,1467590578; Hm_lpvt_f3c68d41bda15331608595c98e9c3915=1467596252; _ga=GA1.2.1767721756.1467443560; gr_session_id_aacd01fff9535e79=8a924b6f-accc-41e3-b0dc-3e35c6b50bfc; gr_cs1_8a924b6f-accc-41e3-b0dc-3e35c6b50bfc=uid%3A5228427; looyu_20001269=v%3Adf260b25526ebda8e71e44d5c1ddb77421%2Cref%3A%2Cr%3A%2Cmon%3Ahttp%3A//m9104.talk99.cn/monitor%2Cp0%3Ahttp%253A//www.jikexueyuan.com/course/2834_2.html; undefined=; stat_isNew=0'}
        wb_data = requests.get (url, headers=header)
        soup = BeautifulSoup (wb_data.text, 'lxml')
        video_tag = soup.select ('source')
        video_source = video_tag[0].get ('src')
        cates = soup.select ('#pager > div.crumbs > div > a')
        videoname_un = soup.select ('title')
        video_name = videoname_un[0].get_text ().split('-极客学院')[0]
        print (video_name)
        folder_temp = folder_base
        for cate in cates[2:]:
            folder_temp += cate.text + '\\'
        print (folder_temp)
        try:
            os.makedirs (folder_temp)
        except:
            pass
        try:
            video.insert ({
                'name': folder_temp+video_name+'.mp4',
                'src': video_source
            })
            print({ 'name': folder_temp+video_name+'.mp4',
                'src': video_source})
        except:
            print('get  ',video_name,' failed! ')
            video_fal.insert({'name':folder_temp+video_name+'.mp4',
                              'video_fal':video_source})
    except Exception as i:
        print('video page parse failed!')
        video_fal.insert ({'video_page_fal': url})

if outer.find().count() < 20:  # 看看课程链接列表中有没有数据，有就不执行
    for url in course_inter:
        get_course_pages (url)
else:
    pass
if inner.find().count() < 20: # 看看课节链接列表中有没有数据，有就不执行
    for o in outer.find():
        url = o['url']
        get_lesson_pages(url)
else:
    pass
if video.find().count() < 5:  # 看看视频链接列表中有没有数据，有就不执行
    for o in inner.find():
        url = o['video_from']
        get_video_srcs(url)
else:
    pass
a = set([i['src'] for i in video.find()])
b = set([u['src'] for u in video_done.find()])
tobedone = a-b  # 这是还没有爬取过的地址列表
for src in tobedone:
    for e in video.find({'src':src}):
        time.sleep(5)
        print('Downloading ',e['name'],'....\n',src)
        try:
            urllib.request.urlretrieve(src,e['name'])   
            video_done.insert({
                'src':e['src'],
                'name':e['name']
            })
        except:
            print('download failed!')
            video_fal.insert({'name':e['name'],'src':src})
