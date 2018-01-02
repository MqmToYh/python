#!/usr/bin/env python 
# -*- coding:utf-8 -*-

import os
import re
from cfg import DBCFG,PATH,courses
from SqlUtil import Mysql
import LoggerUtil
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

logger = LoggerUtil.getLogger(__name__)

def putToDB(fileName,rows = 1000):
    mysql = Mysql()
    try:  
        pos = os.path.getsize(fileName)
        with open(fileName,'r') as f:
            count = 0
            batchSql = None            
            err_Sql = []
            for sql  in f:
                count += 1
                err_Sql.append(sql)
                if batchSql: 
                    batchSql = "%s , %s" %(batchSql, re.findall(u"values(\(.+\));\s*\n$",sql)[0])                                       
                else:
                    batchSql = re.findall(u"^(.+);\s*\n$",sql)[0]                 
                if count % rows == 0:
                    try:            
                        executeSql(mysql,batchSql,fileName,err_Sql,count)       
                    finally:                                
                        err_Sql = []
                        batchSql = None                
            if batchSql:executeSql(mysql,batchSql,fileName,err_Sql,count)  
    except Exception as e:
        logger.exception(u"sql文件名称：%s,错误信息:%s" %(fileName,e.message))
    finally:
        mysql.cancel()
        mysql.close()
def executeSql(mysql,batchSql,fileName,err_Sql,count):
    try:
        mysql.execute(batchSql)
        mysql.commit()                        
        print u"执行%s条SQL" % count
    except Exception  as ex:
        mysql.rollback()
        logger.exception(ex.message)
        writeErrSql(fileName,err_Sql)

def writeErrSql(fileName,err_Sql):
    with open(fileName +'-put.error.sql','a+') as f:f.writelines(err_Sql)
def main(course,path_in=PATH.sql_path_in):
    fileName = os.path.join(path_in,u'%s-%s-%s.sql'%(course['cn'],course['cid'],course['st']))
    putToDB(fileName)

if __name__ == '__main__':
    main(courses['english'][2])