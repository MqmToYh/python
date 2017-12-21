#!/usr/bin/env python
#-*-coding:utf-8-*-

class PATH:
    #文件保存的根路径
    root_path = 'data/'
    #临时文件后缀
    tmp_suffix = "-tmp"
class SQL:
    insert_sql = "INSERT into t_jyeoo_img_url (qid,urls,status) values(%s,%s,%s)"
    select_sql = "SELECT qid,answer,analyses,content,discuss,method,options from  t_jyeoo_ques where status = 0  LIMIT 1000"
    select_sql_img ="SELECT id,qid,urls,status from t_jyeoo_img_url where status = 0 and id > %d order by id LIMIT 1000"
    update_sql = "UPDATE t_jyeoo_ques set status = %s where qid = %s "
    update_sql_img = "UPDATE t_jyeoo_img_url set status = %s where qid = %s "

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



