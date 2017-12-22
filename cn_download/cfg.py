#!/usr/bin/env python
#-*-coding:utf-8-*-

class SQL:
    insert_sql = 'insert into hanyu_font(name,picture,pinyin_info,radical,strokes,traditional,wuxing,wubi,font,definition,basicmean,detailmean) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class PATH:
    #文件保存的根路径
    root_path = 'data/'
    #下载html保存路径
    html_path= root_path+'html/'
    html_zdic_path = root_path+ 'html_zdic/'
    #图片保存路径
    pic_path = root_path+'pic/'
    #语音保存路径
    voice_path= root_path+'voice/'
    #中文文件
    cn_file = root_path+'Chara.gb'
class URLS:
    cn_url = 'http://hanyu.baidu.com/s?wd=%s&ptype=zici'  #ptype=zici

class DBCFG:
    '''Mysql数据库配置'''
    host ="192.168.26.157"
    user ="iread"
    passwd="iread"
    db="iread"
    #host="127.0.0.1"    
    #user="root"    
    #passwd="mqm"   
    #db="hanyun_mqm"
    port=3306
    charset="utf8"
    mincached=1
    maxcached=10
    maxconnections=30
class POSTGRE_CFG:
    '''postgreSql数据库配置'''
    host ="192.168.26.157"
    port = 5432
    user ="iread"
    passwd="iread"
    db="iread"
    #host = "localhost"
    #port = 24967
    #user="root"
    #passwd="pangu"
    #db="ycl_resource"





