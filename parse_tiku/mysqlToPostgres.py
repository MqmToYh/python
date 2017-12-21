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
from cfg import TAB_NAME,SQL_FILE
import sys   
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入   
sys.setdefaultencoding('utf-8') 

logger = LoggerUtil.getLogger(__name__)


def converUnicode(strData):  
    '''转换为Unicode编码, 暂不使用'''  
    return strData.replace(u'\xa0', u' ').encode("utf-8")

if __name__ == "__main__":
    mysql = Mysql()
    sql = "SELECT autoId,OriginalID,Answer,Analysis,Difficulty,difficultyValue, \
	Content,KnowledgeDetail,`Comment`,zujuan_number,`Options`, \
	thirdkonwledgeid,secondknowledgeid,firstknowledgeid,courseId, \
	subject_code,typeflag,typeid,thirdknowledgename \
    FROM "+TAB_NAME+" \
    WHERE  autoId >=(select autoId from "+TAB_NAME+" limit %(start)s,1) limit %(num)s"
    #获取所有的题目数量
    totalnum = mysql.getOne("select count(*) from %s " % TAB_NAME)
    #获取题型
    type_dic= {}
    for row in mysql.getAll('SELECT id,CODE,NAME,cid,ocid FROM tiku_question_type'):
        type_dic[str(row[0])] = {'code':str(row[1]),'name':row[2],'cid':str(row[3])}
    #print type_dic
    #分批迭代加工题目
    autoId = 0
    ignore_num = 0
    flag = 1;
    with open(SQL_FILE+flag,"w") as file:
        for rs in mysql.getIteratorFastAll(sql,totalnum,isdic=True):  
            logger.info(u'加载数据autoId:%s',autoId)           
            for r in rs:    
                if r['typeid'] == '600038': #初中历史选择题，但是有没有选项忽略处理
                    ignore_num +=1
                    continue
                autoId = r['autoId']   #用于标记处理数据的进度         
                qtype = type_dic[r['typeid']] #对应线上题目类型
                points = '[{"code":"%s","name":"%s"}]' % (r['thirdkonwledgeid'],r['thirdknowledgename']) #知识点
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
                    method = r['Answer']
                    answerlist.append("")
                insert_sql = "INSERT INTO t_ques_test(id,qid,answer,\"analyse\",cate,cate_name,content,method,options, points,subject,difficulty,paper_count) VALUES(%s,'%s','%s','%s',%s,'%s','%s','%s','%s','%s',%s,%s,%s);"  %(
                r['OriginalID'],uuid.uuid1(),json.dumps(answerlist),r['Analysis'],qtype['code'],qtype['name'],r['Content'],
                method, r['Options'] if r['Options'] else '[]',points,qtype['cid'],difficultyValue,r['zujuan_number'] )
                file.write(insert_sql + '\n')
                #logger.info(insert_sql)
        mysql.close()
    print u'所有题目:%d,忽略题目:%d，有效题目%d' %(totalnum,ignore_num,totalnum-ignore_num)
    '''
    pm = db.PyMysql()
    conn = pm.getConnection()
    pag = db.MySQLQueryPagination(conn)
    #progresdb = db.PyProgresql()
    pageSql = r'select OriginalID,Options,answer,analysis,Difficulty,Content,zhujuan_number,thirdkonwledgeid,type from k12_tiku_details order by DOCID'
    sql = r'SELECT OriginalID,Options,answer,analysis,Difficulty,Content,zhujuan_number,thirdkonwledgeid,type,thirdknowledgename	FROM k12_tiku_details WHERE DOCID>=(SELECT DOCID FROM k12_tiku_details LIMIT %s,1) LIMIT %s'
    sql_file_object = open('physics.high.postsql.sql',"w")
    i=1
    for ret in pag.queryForList(pageSql,sql,None):
        begin = datetime.datetime.now()
        for data in ret:
            #print data[0],data[1]
            #sql = "insert into t_ques(id,qid,options,answer,analyse) values(%s,'%s','%s','%s','%s') " %(data[0],uuid.uuid1(),data[1],data[2],data[3])
            #sql = "insert into t_ques(id,qid,options,answer,analyse) values(%s,'%s','%s','%s') " %(data[0],uuid.uuid1(),data[1],data[2])
            #print(type(data[2]))
            #146	1	选择题	20
            # #147	2	填空题	20
            #       3   判断题 20
            # #148	9	解答题	20
            # 600012 600013 600014 600015 600016 
            if data[8]=='600012':
                cate = 1
                cateName = '选择题'
            elif data[8]=='600013':
                cate = 1
                cateName = '选择题'
            elif data[8]=='600014':
                cate = 3
                cateName = '判断题'
            elif data[8]=='600015':
                cate = 2
                cateName = '填空题'
            elif data[8]=='600016':
                cate = 9
                cateName = '解答题'
            else:
                cate = 1
                cateName = '选择题' 

            if data[5]!='':
                point_jsonb = '[{"code":\"'+data[7]+'\","name":'+'\"'+data[9]+'\"}]'
                sql = "insert into t_ques(id,qid,options,answer,\"analyse\",difficulty,content,paper_count,\"points\",\"subject\",cate,\"cate_name\") values(%s,'%s','%s','%s','%s',%s,'%s',%s,'%s',%s,%s,'%s'); \n" %(data[0],uuid.uuid1(),data[1],converUnicode(data[2]),converUnicode(data[3]),int(float(data[4])*5),converUnicode(data[5]),data[6],point_jsonb,31,cate,cateName)
                sql_file_object.write(sql)
        sql_file_object.flush()
        end = datetime.datetime.now()
        print 'page number,',i,(end-begin)
        i=i+1
                #try:
                #    progresdb.execute_sql(sql,None)
                #except:
                #    print sql
    conn.close()
    sql_file_object.close()    
    #progresdb.closeConnnection()

'''
