#!/usr/bin/python
#-*-coding:utf-8-*-
import os
import sys
import HTMLParser
from bs4 import BeautifulSoup
import re #引入正则
import json 
from cfg import analysisroot,errPath
reload(sys)
sys.setdefaultencoding('utf-8')
type_coding = sys.getfilesystemencoding()

#html转义字符处理
html_parser = HTMLParser.HTMLParser()

def writeErrSql(courseId, s):
    if not os.path.exists(errPath):
        os.makedirs(errPath)
    with open(errPath + courseId+'_err','a+') as f:
        f.write(s+'\n')

def delComments(line):
    '''
    删除 html文件中的注释 <!--.*?-->
    '''
    re_comment = re.compile("<!--.*?-->")
    line = re_comment.sub("",line)
    return line
    
def get_question_detail(data_id):
    '''获取题目详情，并以Map形式返回结果'''
    analysis_file_name=analysisroot+data_id+"/"+data_id+".html"
    with open(analysis_file_name) as sa:
        html = delComments(sa.read())            
        soup = BeautifulSoup(html,"lxml")
        scripts = soup.find_all(name ="script",attrs={'type':"text/javascript"}, text=re.compile("var\s*vo\s*=\s+(.+?)\s*;\s*with"))
        if not scripts:
            raise Exception(u"获取的网页状态不正常")

        scripts_str = scripts[0].get_text()  
        vo_str = '{'+ re.findall(r"var\s*vo\s*=\s*{(.+?)}\s*,\s*error\s*=",scripts_str)[0] + '}'        
        vo = json.loads(vo_str)      
        sa.close()
        return vo

def fetch_questions(html,knowledgename):
    '''提取html中所有题目'''   
    soup = BeautifulSoup(html_parser.unescape(html),"html.parser")
    lis = soup.find("ul",{"class":"m-list"}).find_all("li")
    stringsBuffer=[]
    stringsError=[]
    for li in lis:  
        data_id = li['data-id'] #试题编码  
        data_cid = li['data-cid'] #课程ID
        try:
            # 替换题干中的图片地址 暂未实现...
            # 替换答案选项中的图片地址 暂未实现...  
            # 替换分析中的图片地址   暂未实现...   
    
            vo = get_question_detail(data_id)  
            opts = ""
            optionHtmlList = vo['optionHtmlList'] if 'optionHtmlList' in vo else ''
            if optionHtmlList :
                rs = re.findall(u'{"optionHtml":"[A|B|C|D|E|F|G]、(.+?)"}[,|\]]',optionHtmlList)
                opts = json.dumps(rs,ensure_ascii=False)          
            sql = "insert into k12_tiku_details(OriginalID,Answer,Analysis,Difficulty,difficultyValue,Content,Options,zujuan_number,thirdkonwledgeid,secondknowledgeid,firstknowledgeid,thirdknowledgename,courseId,typeflag,typeid) \
            values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'); "
            #题目原始ID,答案,分析,难度,内容,选项,组卷次数,三级知识ID,二级知识点ID,一级知识点ID,类型,三级知识名称   
            #print opts.decode(utf-8)
            params = (unicode(vo['id']),vo['answerHtml'],vo['anylysisHtml'],str(vo['difficulty']),str(vo['difficultyValue']),
            vo['bodyHtml'],opts,str(vo['zujuanCount']),
            str(vo['thirdKnowledgeId']),str(vo['secondKnowledgeId']),str(vo['firstKnowledgeId']),knowledgename,
            str(vo['courseId']),str(vo['questionTypeFlag']),str(vo['questionTypeId']))  
  
            stringsBuffer.append(sql % params)
            
        except Exception as e:
            writeErrSql(data_cid,u"生成题目SQL插入语句异常,题目id:%s,错误信息:%s" %(data_id,e.message))
            stringsError.append("{id:%s,cid:%s}" % (data_id,data_cid))
    # 需要将未处理成功的题目ID记录下来 stringsError存入文件
    return stringsBuffer



def parse_html_pg(file,knowledgename):
    '''返回分页题目中所有的插入SQL'''
    try:        
        with open(file) as sa:
            html = sa.read()
            html = delComments(html)
            return fetch_questions(html,knowledgename)            
    except Exception as ex:
        writeErrSql('knowled',u"生成知识点的所有SQL异常,知识点名称:%s,文件路径:%s,错误信息:%s" %(knowledgename,file,ex.message))
        print(ex)
        return []
    



#if __name__ == "__main__":

    #parse_html_pg(path,filename)
