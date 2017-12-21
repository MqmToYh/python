#!/usr/bin/python
#-*-coding:utf-8-*-

knowled_name = {
    "physics":"physics.middle.html",
}

# 爬取题库的主页面
base_url = "http://k12.tiku.com/testPaper.html"

# ([0-章节，1-知识点],[课程中文名称],[0-小学，1-初中，2-高中],[课程源编码])
url_suffix = '?hdSearch=&key=&sct=%s&cn=%s&st=%s&cid=%s'

courses ={
    "math":[{'st':'0','scid':'500014','cid':'10','cn':'数学'},{'st':'1','scid':'500010','cid':'20','cn':'数学'},{'st':'2','scid':'500004','cid':'30','cn':'数学'}],
    "chinese":[{'st':'0','scid':'500021','cid':'16','cn':'语文'},{'st':'1','scid':'500020','cid':'26','cn':'语文'},{'st':'2','scid':'500019','cid':'36','cn':'语文'}],
    "english":[{'st':'0','scid':'500023','cid':'17','cn':'英语'},{'st':'1','scid':'500024','cid':'27','cn':'英语'},{'st':'2','scid':'500022','cid':'37','cn':'英语'}],

    "physics":[{},{'st':'1','scid':'500012','cid':'21','cn':'物理'},{'st':'2','scid':'500011','cid':'31','cn':'物理'}],
    "chemistry":[{},{'st':'1','scid':'500015','cid':'22','cn':'化学'},{'st':'2','scid':'500016','cid':'32','cn':'化学'}],
    "biology":[{},{'st':'1','scid':'500007','cid':'23','cn':'生物'},{'st':'2','scid':'500013','cid':'33','cn':'生物'}],
   
    "geography":[{},{'st':'1','scid':'500005','cid':'25','cn':'地理'},{'st':'2','scid':'500009','cid':'35','cn':'地理'}],
    "politics":[{},{'st':'1','scid':'500006','cid':'28','cn':'思品'},{'st':'2','scid':'500008','cid':'38','cn':'政治'}],
    "history":[{},{'st':'1','scid':'500018','cid':'29','cn':'历史'},{'st':'2','scid':'500017','cid':'39','cn':'历史'}]
}

sql_temp ={
    'section':'insert into tiku_section_relation(id,name,level,parentId,sortNo,vid,bid,cid) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
    'knowled':'insert into tiku_knowled_relation(id,name,level,parentId,sortNo,cid) VALUES(%s,%s,%s,%s,%s,%s)',
    'questionType':'insert into tiku_question_type(id,name,cid,ocid) VALUES(%s,%s,%s,%s)',
}

db_cofig={
    "host":"127.0.0.1",
    "user":"root",
    "passwd":"mqm",
    "db":"tiku_mqm",
    "port":3306
}