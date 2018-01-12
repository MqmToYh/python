#!/usr/bin/python
#-*-coding:utf-8-*-
'''
生成mysql的SQL文件
generate all sql file
'''
import os
import time
#import hashlib
from bs4 import BeautifulSoup #lxml解析器
import re #正则
import HTMLParser #处理html编码字符 
import threading #线程处理
import json
from multiprocessing import Pool,Lock
import LoggerUtil
import cfg 
import sys 
reload(sys)  
sys.setdefaultencoding('utf8')

logger = LoggerUtil.getLogger(__name__)
  
def parseQuestion(fileName,course):
    '''分析题目'''
    with open(fileName,'r') as f:
        html = f.read()
    try:
        #获取题目vo对象
        soup = BeautifulSoup(html,"lxml")
        scripts = soup.find_all(name ="script",attrs={'type':"text/javascript"}, text=re.compile("var\s*vo\s*=\s+(.+?)\s*;\s*with"))
        if not scripts: raise Exception(u"获取的网页状态不正常")
        try:
            vo = json.loads(vo_str)
        except Exception as ex:
            vo = json.loads(vo_str.replace('\t','\\t')) 
        vo_tm = {}
        for key, value in vo.items(): 
            if isinstance(value,(str,unicode)):
                vo_tm[key] = value.replace("\\","\\\\").replace("'","\\'")
            else:
                vo_tm[key] = value
        vo = vo_tm
        # 替换题干中的图片地址 暂未实现...
        # 替换答案选项中的图片地址 暂未实现...  
        # 替换分析中的图片地址   暂未实现... 
        opts = ""
        optionHtmlList = vo['optionHtmlList'] if 'optionHtmlList' in vo else ''
        if optionHtmlList == "[]":
            opts = optionHtmlList
        elif optionHtmlList :
            rs = re.findall(u'{"optionHtml":"[A|B|C|D|E|F|G]、(.+?)"}[,|\]]',optionHtmlList)
            #处理另一种格式的选项
            if not rs: rs=re.findall(u'{"optionHtml":"&lt;p&gt;.+?&lt;/span&gt;(.+?)&lt;/p&gt;\s*"}[,|\]]',optionHtmlList)
            if not rs: logger.info(vo_str)
            rs_a = []
            #处理选择中有table结束标签没有开始标签的题目
            for opt in rs:
                pattern = u'&lt;/td&gt;\s*&lt;/tr&gt;\s*(&lt;/tbody&gt;)?\s*&lt;/table&gt;'
                option= opt if opt.find('&lt;table/&gt;') > -1 else re.sub(pattern,'',opt)
                rs_a.append(option)
            opts = json.dumps(rs_a,ensure_ascii=False)
            opts = opts.replace("'","\\'")   
        sql = u"insert into k12_tiku_details(OriginalID,Answer,Analysis,Difficulty,difficultyValue,Content,Options,zujuan_number,thirdkonwledgeid,secondknowledgeid,firstknowledgeid,courseId,subject_code,typeflag,typeid) \
        values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,'%s','%s'); \n"
        #题目原始ID,答案,分析,难度,内容,选项,组卷次数,三级知识ID,二级知识点ID,一级知识点ID,类型,三级知识名称   
        #print opts.decode(utf-8)
        #修复题干right样式没有引号
        bodyHtml = re.sub(u'&lt;div\s+align=right&gt;(.*?)&lt;/div&gt;','',vo['bodyHtml'])
        #修复多括号乱码
        bodyHtml = re.sub(u'([^（])（ ））','\g<1>（）',bodyHtml)
        vo['difficulty'] =  vo['difficulty'] if 'difficulty' in vo else int(vo['difficultyValue']*3)
        params = (unicode(vo['id']),vo['answerHtml'],vo['anylysisHtml'],str(vo['difficulty']),str(vo['difficultyValue']),
        bodyHtml,opts,str(vo['zujuanCount']),
        str(vo['thirdKnowledgeId']),str(vo['secondKnowledgeId']),str(vo['firstKnowledgeId']),
        str(vo['courseId']),course['cid'],str(vo['questionTypeFlag']),str(vo['questionTypeId']))
        return sql % params        
    except Exception as e:
        logger.exception(u"生成题目SQL插入语句异常,题目与一级知识点id:%s,课程Id:%s-%s,错误信息:%s" %(os.path.basename(fileName),course['cid'],course['scid'],e.message))
        return ''
def parseQuestions(filenames,course,sqlfile):
    try:
        file_num = len(filenames)
        print u'开始处理%d个文件'% file_num
        strs = map(lambda x:parseQuestion(x,course),filenames)        
        try:
            lock.acquire()
            with open(sqlfile,'a+') as f:f.writelines(strs)
        finally:
            lock.release()
        print u'处理完成%d个文件，成功处理%d文件' % (file_num,len(strs)) 
    except Exception as e:
        logger.exception('批量处理%d个题目文件异常，异常信息:%s,处理文件%s'%(file_num,e.message,json.dumps(filenames,ensure_ascii=False)))
        logger.error('--sql---\n%s',"\n".join(strs))
        

def parseCourse(course,pool):
    scid = course['scid']
    cn = course['cn']
    sqlfile = os.path.join(cfg.PATH.sql_path,u'%s-%s-%s.sql'%(cn,course['cid'],course['st']))
    question_path = os.path.join(cfg.PATH.root_path, u"%s-%s/questions" %(scid,cn))
    with open(sqlfile,'w+'): pass
    semaphore=threading.Semaphore(cfg.semaphoreMax)
    filenames = []
    count = 0  
    for fileName in os.listdir(question_path):
        filenames.append(os.path.join(question_path,fileName))
        count +=1
        if len(filenames) >= 1000:            
            pool.apply_async(parseQuestions,(filenames,course,sqlfile))            
            print u'已添加到进程池的数目%d' % count
            filenames = []
    if filenames:
        pool.apply_async(parseQuestions,(filenames,course,sqlfile))
        print u'已添加到进程池的数目%d' % count

def init(l):
    '''进程初始化全局的锁'''
    global lock
    lock = l
def main():
    '''分析所有的题目'''
    lock = Lock()
    
    pool = Pool(processes=3,initializer=init,initargs=(lock,))
    for key, value in cfg.courses.items():
        for course in value:
            if course:
                parseCourse(course,pool)
    pool.close()
    pool.join()

if __name__ == "__main__":    
    if not os.path.exists(cfg.PATH.sql_path):
        os.makedirs(cfg.PATH.sql_path)
    '''分析所有的题目'''
    #main()
    #分拆为每个课程分析
    lock = Lock()
    pool = Pool(processes=3,initializer=init,initargs=(lock,))
    #parseCourse(cfg.courses['physics'][2],pool)
    pool.close()
    pool.join()

    

