#!/usr/bin/env python
#-*-coding:utf-8-*-


#课程
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
semaphoreMax=20
TAB_NAME = 'k12_tiku_details'
class PATH:
    #文件保存的根路径
    root_path = '../k12_tiku_scrapy/data/'
    #图片保存路径
    pic_path = '../k12_tiku_scrapy/data/pic/'
    #生成的SQL文件保存路径
    sql_path = '../../download_sql/new_sql/'
    #导入的SQL文件保存路径
    sql_path_in = '../../download_sql/new_sql/'
    #未下载文件后缀 
    tmp_suffix = '-tmp'
'''配置类'''
class DBCFG:
    '''Mysql数据库配置'''
    host ="127.0.0.1"
    user ="root"
    passwd="mqm"
    db="tiku_mqm"
    port=3306
    charset="utf8"
    mincached=1
    maxcached=10
    maxconnections=30
class POSTGRE_CFG:
    '''postgreSql数据库配置'''
    host = "localhost"
    port = 24967
    user="root"
    passwd="pangu"
    db="ycl_resource"



