#!/usr/bin/python
#-*-coding:utf-8-*-
'''
生成mysql的SQL文件
generate all sql file
'''
import os
import time
import hashlib
from bs4 import BeautifulSoup #lxml解析器
import re #正则
import HTMLParser #处理html编码字符 
import tiku_Parser
import threading #线程处理
from cfg import subjectfilename, contentroot,analysisroot,sqlPath
import sys 
reload(sys)  
sys.setdefaultencoding('utf8')



def startStrs(*startstring):
        starts = startstring
        def run(s):
            '''返回符合规定字符开始的字符串 '''
            f = map(s.startswith,starts)
            if True in f: return s
        return run

def handleSqlFile(tknowledgeid,tknowledgename,sqlfile):    
    list_file = os.listdir(contentroot)
    a = startStrs(tknowledgeid)   
    #获取以三级知识点ID开始的的文件 分页文件集合
    f_file = filter(a,list_file)
    #此处应该还要分析哪些Pg页面没有下载下来
    sqlBuffer=[]
    for filename in f_file: 
        data = tiku_Parser.parse_html_pg(contentroot+filename,tknowledgename)
        if data:
            sqlBuffer.extend(data)  
    if sqlBuffer:
        print "generat file:%s" % sqlfile
        with open(sqlfile,'w') as sa:
            sa.write("\n".join(sqlBuffer))
    
class parseSqlCls (threading.Thread):
    def __init__(self, semaphore,tknowledgeid,tknowledgename,sqlfile):
        threading.Thread.__init__(self)        
        self.semaphore = semaphore
        self.tknowledgeid = tknowledgeid
        self.tknowledgename = tknowledgename
        self.sqlfile = sqlfile
    
    def run(self):
        with self.semaphore:
        #self.semaphore.acquire()  
            handleSqlFile(self.tknowledgeid,self.tknowledgename,self.sqlfile)
        #self.semaphore.release()  

if __name__ == "__main__":    
    file_object = open(subjectfilename)
    #设置信号量同时进行最大线程数量
    semaphore = threading.Semaphore(50) 
    if not os.path.exists(sqlPath):
        os.makedirs(sqlPath)
    try:
        all_the_text = file_object.read( )
        html_parser = HTMLParser.HTMLParser()
        response_selector = BeautifulSoup( html_parser.unescape(all_the_text),"lxml")
        for top in response_selector.find_all('li',{"class": "tree-node-0"}):                 
            for second in top.find_all('dl',{"class": "z-open"}):                 
                for divtag in second.find_all('dd', {"class": "tree-node-2"}):                                       
                    tknowledgeid = divtag.a['data-id']
                    tknowledgename = divtag.a['title']
                    sqlfile = sqlPath +  "chemistry.middle_"+tknowledgeid+".sql"
                    if not os.path.exists(sqlfile):
                        t = parseSqlCls(semaphore,tknowledgeid,tknowledgename,sqlfile) 
                        t.start() 
        #等待所有线程结束 
        for t in threading.enumerate(): 
            if t is threading.currentThread():
                continue
            t.join() 
    finally:
        file_object.close( )
    
    

