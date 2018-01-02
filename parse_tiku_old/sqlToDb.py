#!/usr/bin/env python
#-*-coding:utf-8-*-
'''
将SQL文件导入到Mysql数据中并记录导入不成功的SQL
'''
import os
import threading 
from SqlUtil import Mysql
import LoggerUtil
from cfg import errSqlPath,sqlfiledir
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

logger = LoggerUtil.getLogger(__name__)
class dbThread (threading.Thread):
    def __init__(self, semaphore,filename):
        threading.Thread.__init__(self)
        self.semaphore = semaphore
        self.filename = filename
    
    def run(self):
        with self.semaphore:          
            print "start insert file %s " % self.filename 
            logger.info("start insert file %s " % self.filename)          
            sqlToDb(self.filename) 
            logger.info("end insert file %s " % self.filename)      
            print "end insert file %s " % self.filename

def sqlToDb(filename):
    '''插入SQL按一条条的SQL进行插入'''
    mysql =  Mysql(True)
    try:                
        with open(filename, "r") as f:
            for sql in f:
                try:
                    mysql.execute(sql,None)
                    #mysql.commit()
                except Exception as ex:
                    logger.error(ex.message)
                    writeErrSql(sql)
    except Exception as e:
        logger.error(u"sql文件名称：%s,错误信息:%s" %(filename,e.message))
    finally:
        mysql.cancel()
        mysql.close()

def writeErrSql(sql):
    if not os.path.exists(errSqlPath):
        os.makedirs(errSqlPath)
    with open(errSqlPath + 'error.sql','a+') as f:
        f.write(sql)   

if __name__ == "__main__":    
    semaphore = threading.Semaphore(10) 
    for root, dirs, files in os.walk(sqlfiledir):
        for file in files:
            filename = os.path.join(root, file)
            t = dbThread(semaphore,filename) 
            t.start()
            #等待所有线程结束 
        for t in threading.enumerate(): 
            if t is threading.currentThread(): 
                continue
        t.join()
    
