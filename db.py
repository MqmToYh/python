
#!/usr/bin/env python
#-*-coding:utf-8-*-
import MySQLdb
import pubcfg
import psycopg2
import sys
import datetime
reload(sys) 
sys.setdefaultencoding('utf-8')   


def initClientEncode(conn):
    '''mysql client encoding=utf8'''
    curs = conn.cursor()
    curs.execute("SET NAMES utf8")
    conn.commit()
    return curs

class PyMysql:
    def __init__(self):
        self.conn = MySQLdb.connect(pubcfg.MYSQL_CONFIG_MAP["host"], pubcfg.MYSQL_CONFIG_MAP["user"], pubcfg.MYSQL_CONFIG_MAP["passwd"], pubcfg.MYSQL_CONFIG_MAP["db"], charset="utf8")
    
    def test(self):
        print "text"
    
    def newConnection(self, host, user, passwd, defaultdb):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.defaultdb = defaultdb
        self.conn = MySQLdb.Connect(host,user,passwd,defaultdb)
        self.conn.set_character_set('utf8')
        if self.conn.open == False:
            raise None
        
    def closeConnnection(self):
        self.conn.close()


    def getConnection(self):
        return self.conn
    

    def execute_sql(self,sql,params):
        try:
            self.conn.cursor().execute(sql,params)
            self.conn.commit()
        except MySQLdb.Error, e:
            print "error: %d, %s" % (e.args[0], e.args[1])
            print sql
            self.conn.rollback()



class PyProgresql:
    def __init__(self):
        self.conn = psycopg2.connect(database='ycl_resource',user='root',password='pangu',host='127.0.0.1',port='24967')  
        self.conn.set_client_encoding('utf-8')
    

    def getConnection(self):
        return self.conn
  
        
    def closeConnnection(self):
        self.conn.close()

    def execute_sql(self,sql,params):
        try:
            self.conn.cursor().execute(sql,params)
            self.conn.commit()
        except psycopg2.Error ,e:
            #print "error: %d, %s" % (e.args[0], e.args[1])
            print "error: occured",e
           
            self.conn.rollback() 

class MySQLQueryPagination(object):
    
    def __init__(self,conn,numPerPage = 1000):
        self.conn = conn
        self.numPerPage = numPerPage
    
    def queryForList(self,pageSql,sql,param = None):
        totalPageNum = self.__calTotalPages(pageSql,param)
        for pageIndex in range(totalPageNum):
            yield self.__queryEachPage(sql,pageIndex,param)
        
    def __createPaginaionQuerySql(self,sql,currentPageIndex):
        startIndex = self.__calStartIndex(currentPageIndex)
        qSql  = sql % (startIndex,self.numPerPage)
        return qSql
    
    def __queryEachPage(self,sql,currentPageIndex,param = None):
        curs = initClientEncode(self.conn) 
        qSql = self.__createPaginaionQuerySql(sql, currentPageIndex)   
        print qSql   
        begin = datetime.datetime.now()
        curs.execute(qSql,param)
        result = curs.fetchall()
        curs.close()
        print 'execut sql time is ',datetime.datetime.now()-begin,qSql
        return result
    
    def __calStartIndex(self,currentPageIndex):
        startIndex = currentPageIndex  * self.numPerPage;
        return startIndex;
    
    def __calTotalRowsNum(self,sql,param = None):
        tSql = r'select count(*) from (%s) total_table' % sql
        curs = initClientEncode(self.conn) 
        if param is None:
            curs.execute(tSql)
        else:
            curs.execute(tSql,param)
        result = curs.fetchone()
        curs.close()
        totalRowsNum = 0
        if result != None:
            totalRowsNum = int(result[0])
        
        return totalRowsNum
    
    def __calTotalPages(self,sql,param):
        totalRowsNum = self.__calTotalRowsNum(sql,param)
        totalPages = 0;
        if (totalRowsNum % self.numPerPage) == 0:
            totalPages = totalRowsNum / self.numPerPage;
        else:totalPages = (totalRowsNum / self.numPerPage) + 1 
        return totalPages
    
    def __calLastIndex(self, totalRows, totalPages,currentPageIndex):
        lastIndex = 0;
        if totalRows < self.numPerPage:
            lastIndex = totalRows;
        elif ((totalRows % self.numPerPage == 0)or (totalRows % self.numPerPage != 0 and currentPageIndex < totalPages)) :
            lastIndex = currentPageIndex * self.numPerPageel
        if (totalRows % self.numPerPage != 0 and currentPageIndex == totalPages): 
            lastIndex = totalRows         
        return lastIndex
