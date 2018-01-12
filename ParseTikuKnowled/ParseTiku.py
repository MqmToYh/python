#!/usr/bin/python
#-*-coding:utf-8-*-

import threading # 线程处理
import HTMLParser #处理html编码字符
from bs4 import BeautifulSoup #lxml解析器
import urllib #url 请求
import re #正则
import json #json
import MySqlUtil #引入SQL工具方法
import time 
import sys #设置系统属性
reload(sys)  
sys.setdefaultencoding('utf8')
#导入系统配置
from config import base_url, knowled_name, url_suffix, courses, sql_temp

type_coding = sys.getfilesystemencoding()
html_parser = HTMLParser.HTMLParser() 
class ParseTiku:
    '''
        分析题库（学科或知识点的）主页面
    '''

   
    def parseKnowled(self,course_dic):
        '''
        按知识点分析学科主方法        
        '''  
        course_url = base_url + url_suffix % (1,urllib.quote(course_dic['cn']),course_dic['st'],course_dic['scid'])  
        print "知识点请求地址：".encode(type_coding) + course_url  
        #获取网页内容
        all_the_text = urllib.urlopen(course_url).read()       
        #lxml HTML 解析器      
        subject_selector = BeautifulSoup(html_parser.unescape(all_the_text),"lxml")
        courseId = re.findall(r"cid=(.+?)$",course_url)[0]  
        sql_params =[]     
        sortNo = 0
        for first_selector  in subject_selector.find_all('li',{"class":"tree-node tree-node-0 z-open"}):            
            first_title = first_selector.a["title"]
            first_id = re.findall(r"ftid=(.+?)&",first_selector.a["href"])[0]
            sql_params.append((first_id,first_title,1,None,sortNo,course_dic['cid']))      
            sortNo += 1
            sortNo_s = 0
            for second_selector in first_selector.find_all('dl'):                   
                second_title = second_selector.dt.a["title"]      
                second_id = second_selector.dt['data-id']   
                sql_params.append((second_id,second_title,2,first_id,sortNo_s,course_dic['cid']))  
                sortNo_s += 1
                # post 请求  courseId:500012 parentId:705867 此为ajax请求的子菜单json数据
                second_url = "http://k12.tiku.com/service/knowledge/findKnowledgeByCourseAndParentId"
                params = {  
                    'courseId': courseId,  
                    'parentId': second_id,  
                };  
                params = urllib.urlencode(params)  
                childe_text = urllib.urlopen(second_url,params).read()   
                knowleds_json =json.loads(childe_text)
                #print knowled_json["object"]
                for knowled  in knowleds_json["object"] :             
                    third_title = knowled["knowledgeName"]
                    third_id = knowled["id"]
                    sql_params.append((third_id,third_title,3,second_id,knowled["sortNo"],course_dic['cid']))   
            if len(sql_params) >1000 :
                self.__executeSQL__(sql_temp['knowled'],sql_params)
                sql_params=[]
        self.__executeSQL__(sql_temp['knowled'],sql_params)

    def parselocalKnowled(self,course_name):
        '''按知识点分析学科主方法 - 本地文件'''
        # 打开要分析的学科文件
        file_subject = open(course_name)        
        try:
            all_the_text = file_subject.read() #获取文件的所有内容
            #lxml HTML 解析器      
            subject_selector = BeautifulSoup(html_parser.unescape(all_the_text),"lxml")
            for first_selector in subject_selector.find_all('li',{"class":"tree-node tree-node-0 z-open"}):
                for second_selector in first_selector.find_all('dl',{"class": "z-open"}):           
                    for third_selector in second_selector.find_all('dd', {"class": "tree-node-2"}):
                        first_id = third_selector.a["data-ftid"]
                        first_title = first_selector.a["title"]
                        second_id = third_selector.a["data-sid"]
                        second_title = second_selector.dt.a["title"]
                        third_id = third_selector.a["data-id"]
                        third_title = third_selector.a["title"]
                        print first_title,first_id,second_title,second_id,third_title,third_id
        finally:
            file_subject.close() 
    
    def parseSection(self,course_dic):
        '''
        按章节分析学科
        '''         
        course_url = base_url + url_suffix % (0,urllib.quote(course_dic['cn']),course_dic['st'],course_dic['scid'])
        print "章节请求地址：".encode(type_coding) + course_url  
        all_the_text = urllib.urlopen(course_url).read()         
        main_selector = BeautifulSoup(html_parser.unescape(all_the_text),"lxml")
        v_url_suffix = "&vid=%s&sort=0"        
        
        for dd in main_selector.find_all('div',{"id":"filter-version"})[0].find_all('dd'):
            vid = dd["data-id"] #版本ID   
            vname = dd.a.get_text()  #版本名称        
            v_selector = BeautifulSoup(html_parser.unescape(urllib.urlopen(course_url + v_url_suffix % vid).read() ),"lxml")
            for a in v_selector.find_all('div',{"id":"filter-book"})[0].find_all('a'):
                bid = re.findall(r"bid=(.+?)&",a["href"])[0]
                bname = a.get_text() #课本名称 
                # 分析指定版本、指定课本的页面             
                self.__parseSectionVBUrl__(course_url,bid,bname,vid,vname,course_dic['cid'])
        
    def __parseSectionVBUrl__(self,course_url,bid,bname,vid,vname,cid):
        '''
        按章节分析学科指定版本、指定课本的主页面
        '''
        #生成不同版本、不同课本的url  
        b_url_suffix =  "&bid=%s&vid=%s&sort=0" 
        vb_url = course_url + b_url_suffix % (bid,vid) 
        print "章节版本、课本请求地址：".encode(type_coding) + vb_url  
        b__selector = BeautifulSoup(html_parser.unescape(urllib.urlopen(vb_url).read() ),"lxml") 
        sortNo = 0
        #sqlBuff = []
        params = []
        for li in b__selector.find_all('li',{"class":"tree-node tree-node-0 z-open"}):
            uid = re.findall(r"uid=(.+?)&",li.a["href"])[0]#单元ID
            uname = li.a["title"] #单元名称              
            params.append((uid,uname,1,None,sortNo,vid,vname,bid,bname,cid))
            sortNo += 1
            sortNo_c = 0
            for dl in li.find_all('dl'):
                cptid = re.findall(r"cptid=(.+?)&", dl.dt.a["href"])[0] #子单元ID
                cptname = dl.dt.a["title"] #子单元名称               
                params.append((cptid,cptname,2,uid,sortNo_c,vid,vname,bid,bname,cid))
                sortNo_c +=1
                sortNo_k = 0
                for dd in dl.find_all('dd',{"class":"tree-node-2"}):
                    kid = re.findall(r"kid=(.+?)&",dd.a["href"])[0] #知识点ID
                    kname = dd.a["title"] #知识点名称  
                    params.append((kid,kname,3,cptid,sortNo_c,vid,vname,bid,bname,cid))
                    sortNo_k += 1
       
            if len(params) >1000 :
                self.__executeSQL__(sql_temp['section'],params)
                params=[]
        self.__executeSQL__(sql_temp['section'],params) 

    def __executeSQL__(self,sql,params):
        '''用于批量执行SQL'''
        try:    
            start_time  = time.time()                
            MySqlUtil.batchExecute(sql,params)            
            MySqlUtil.commit() 
            print "执行SQL时间:%f,插入数据:%d".encode(type_coding) % (time.time() - start_time,len(params))           
        except Exception, e:
            print "insert sql error!"
            MySqlUtil.rollback()
            raise e


    def parseQuestionType(self,course_dic):
        '''
        分析页面题型    
        '''  
        course_url = base_url + url_suffix % (1,urllib.quote(course_dic['cn']),course_dic['st'],course_dic['scid'])  
        print u"分析页面题型用知识点请求地址："+ course_url  
        #获取网页内容
        all_the_text = urllib.urlopen(course_url).read()       
        #lxml HTML 解析器      
        soup = BeautifulSoup(html_parser.unescape(all_the_text),"lxml")
        courseId = re.findall(r"cid=(.+?)$",course_url)[0]  
        sql_params =[]   

        for dd in soup.find_all('div',{"id":"fitler-tixing-2"})[0].find_all('dd'):
            qre = re.findall(r"&qtid=(.+?)$",dd.a["href"])
            if qre :
                qtid = qre[0]
                sql_params.append((qtid,dd.get_text(),course_dic['cid'],courseId))      
        self.__executeSQL__(sql_temp['questionType'],sql_params)


if __name__=="__main__":
  

    #ParseTiku().parselocalKnowled(knowled_name["physics"])

    #单个页面分析
    #ParseTiku().parseKnowled(courses['math'][1]) 
    #ParseTiku().parseSection(courses['physics'][2])


    #所有页面分析
    parseTiku = ParseTiku()
    for key,values in courses.items():
        for val in values:
            if val:
                #try:
                #    parseTiku.parseKnowled(val)
                #except Exception :
                #    print "Knowled-error:", val
                try:
                    parseTiku.parseSection(val)
                except Exception :
                    print "Section-error:", val
 

    #分析题型
    #ParseTiku().parseQuestionType(courses['chemistry'][2])
    '''
    parseTiku = ParseTiku()
    for key,values in courses.items():
        for val in values:
            if val:
                try:
                    parseTiku.parseQuestionType(val)
                except Exception :
                    print "QuestionType-error:", val
    ''' 

    #使用多线程       
    '''              
    t1 = threading.Thread(target= ParseTiku.parseSection,args=(ParseTiku(),select_url["physics"]))
    t1.start()
    print t1
    for t in threading.enumerate():
        print t
        t.join()
    '''


