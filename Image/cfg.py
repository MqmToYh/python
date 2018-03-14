#!/usr/bin/env python
#-*-coding:utf-8-*-

class PATH:
    #文件保存的根路径
    root_path = 'data/'
    #临时文件后缀
    tmp_suffix = "-tmp"
    pic_new_path = 'data/new/'
start_time = 0.0
image_url = 'http://image.yuncelian.com/1/2017/12/'
class SQL:
    select_sql_img ="SELECT id,qid,urls,status from t_jyeoo_img_url where status = 0 and id > %d order by id LIMIT 1000"
    update_sql_img = "UPDATE t_jyeoo_img_url set status = %s where qid = %s "
    update_sql = "UPDATE t_jyeoo_ques set url_relation  = %s, status = %s where qid = %s "
    insert_sql_convert = 'INSERT INTO t_jyeoo_image_convert(old_jyeoo_url,new_jyeoo_url) values(%s,%s)'

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
    #host= "10.10.6.80"
    port = 24967
    user="root"
    passwd="pangu"
    db="ycl_resource"



