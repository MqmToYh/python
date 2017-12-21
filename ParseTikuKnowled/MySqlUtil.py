#!/usr/bin/python
#-*-coding:utf-8-*-
import MySQLdb #引入mysql数据库驱动包
from config import db_cofig

class MysqlUtil:
    def __init__(self):
        self.conn = self.connect()
        self.cur = self.conn.cursor()
        
    def connect(self):
        '''获取连接'''
        try:
            conn =  MySQLdb.connect(db_cofig["host"], db_cofig["user"], db_cofig["passwd"], db_cofig["db"], charset="utf8")
        except Exception,ex:
            print "mysql conn error"
            raise ex
        return conn
        
    def close(self):
        """关闭当前连接"""
        self.conn.close()

    def execute(self,sql,params=None):
        '''执行SQL'''      
        self.cur.execute(sql,params)
        
    
    def batchExecute(self,sql,params):
        '''执行批处理SQL'''
        self.cur.executemany(sql, params) 

    def commit(self):
        '''提交事务 '''
        self.conn.commit()

    def rollback(self):
        """回滚数据"""
        self.conn.rollback()

     
__util__ = MysqlUtil()
close = __util__.close
commit = __util__.commit
rollback = __util__.rollback
execute = __util__.execute
batchExecute =__util__.batchExecute
