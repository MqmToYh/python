#!/usr/bin/env python
#-*-coding:utf-8-*-

import os 
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import uuid
# import datetime
import LoggerUtil
import json
from SqlUtil import Mysql
from cfg  import TAB_NAME,courses,PATH
import sys   
reload(sys)   
sys.setdefaultencoding('utf-8') 

logger = LoggerUtil.getLogger(__name__)

def mysqlToPostGreSQL(course,tab_name=TAB_NAME):
    mysql = Mysql()    
    sql = "SELECT autoId,OriginalID,Answer,Analysis,Difficulty,difficultyValue, \
	Content,KnowledgeDetail,`Comment`,zujuan_number,`Options`, \
	thirdkonwledgeid,secondknowledgeid,firstknowledgeid,courseId, \
	subject_code,typeflag,typeid \
    FROM "+tab_name+" \
    WHERE  autoId >=(select autoId from "+tab_name+" limit %(start)s,1) limit %(num)s"
    #获取所有的题目数量
    totalnum = mysql.getOne("select count(*) from %s " % tab_name)
    #获取题型
    type_dic= {}
    for row in mysql.getAll('SELECT id,CODE,NAME,cid,ocid FROM tiku_question_type'):
        type_dic[str(row[0])] = {'code':str(row[1]),'name':row[2],'cid':str(row[3])}
    
    #获取知识点
    knowled_dic ={}
    for row in mysql.getAll('SELECT id,name FROM tiku_knowled_relation'): 
        knowled_dic[str(row[0])] = row[1]
    #分批迭代加工题目
    autoId = 0
    #忽略数
    ignore_num = 0
    #文件名
    fileName = os.path.join(PATH.sql_path,u'%s-%s-%s-Postgre.sql'%(course['cn'],course['cid'],course['st']))
    with open(fileName,"w") as file:
        for rs in mysql.getIteratorFastAll(sql,totalnum,isdic=True):  
            logger.info(u'加载数据autoId:%s',autoId)           
            for r in rs:
                if r['typeid'] == '600038' or r['typeid'] == '600112' or r['thirdkonwledgeid'] == '701085' or r['thirdkonwledgeid'] in ['709410','709417','709415','709422','709409','709412','709420','709407','709416','709405','709418','709419'] or r['thirdkonwledgeid'] in ['709479','709489','709491','709486','709495','709487','709480','709496','709488']: 
                    #初中历史选择题，但是有没有选项忽略处理  初中数学三级知识点701085题目有问题，已被原网站舍弃，所以忽略
                    #初中语文三级知识'709410','709417','709415','709422','709409','709412','709420','709407','709416','709405','709418','709419'已被原网站舍弃，所以忽略
                    #高中语文三级知识'709479','709489','709491','709486','709495','709487','709480','709496','709488'已被原网站舍弃，所以忽略，
                    #高中语文题目类型600112被忽略
                    ignore_num +=1
                    continue
                autoId = r['autoId']   #用于标记处理数据的进度         
                qtype = type_dic[r['typeid']] #对应线上题目类型
                try:
                    points = '[{"code":"%s","name":"%s"}]' % (r['thirdkonwledgeid'],knowled_dic[r['thirdkonwledgeid']]) #知识点
                except Exception as e:
                    logger.info(r)
                    raise e
                difficultyValue = str(int(float(r['difficultyValue'])*5)) #难度
                answerlist = []
                method = ""
                if r['typeflag'] == '0':
                    answerlist.append(r['Answer'])
                elif r['typeflag'] == '1':
                    answerlist.extend(r['Answer'].split(','))
                elif r['typeflag'] == '2':
                    answerlist.append( '√' if r['Answer'] == '1' else '×' )
                else:
                    method = r['Answer'].replace("'","''")
                    answerlist.append("")
                insert_sql = "INSERT INTO t_ques(id,qid,answer,\"analyse\",cate,cate_name,content,method,options, points,subject,difficulty,paper_count) VALUES(%s,'%s','%s','%s',%s,'%s','%s','%s','%s','%s',%s,%s,%s);"  %(
                r['OriginalID'],uuid.uuid1(),json.dumps(answerlist).replace("'","''"),r['Analysis'].replace("'","''"),qtype['code'],qtype['name'],r['Content'].replace("'","''"),
                method, r['Options'].replace("'","''") if r['Options'] else '[]',points,qtype['cid'],difficultyValue,r['zujuan_number'] )
                file.write(insert_sql + '\n')
                #logger.info(insert_sql)
        mysql.close()
    print u'所有题目:%d,忽略题目:%d，有效题目%d' %(totalnum,ignore_num,totalnum-ignore_num)


if __name__ == "__main__":    
    #课程
    course =courses['english'][2]
    #读取数据的表名
    tab_name = 'k12_tiku_details_english_high' 
    mysqlToPostGreSQL(course,tab_name)
