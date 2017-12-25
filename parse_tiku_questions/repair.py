#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import urllib2
from bs4 import BeautifulSoup #lxml解析器
import re
import json
import socket
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
socket.setdefaulttimeout(20)

def downloadFile(fileName):
    basename = os.path.basename(fileName)
    questionId = basename.split('-')[0]
    url = u'http://k12.tiku.com/question.html?sct=1&cn=数学&st=2&id=%s&courseId=500004' % questionId
    req=urllib2.Request(url)
    html = urllib2.urlopen(req).read() 
    #获取题目vo对象
    soup = BeautifulSoup(html,"lxml")
    scripts = soup.find_all(name ="script",attrs={'type':"text/javascript"}, text=re.compile("var\s*vo\s*=\s+(.+?)\s*;\s*with"))
    if not scripts: raise Exception(u"获取的网页状态不正常")
    vo_str = re.findall(r"var\s*vo\s*=\s*({.+?})\s*,\s*error\s*=",scripts[0].get_text())[0]
    try:
        vo = json.loads(vo_str)
    except Exception as ex:
        vo = json.loads(vo_str.replace('\t','\\t'))
    if str(vo['id']) == questionId:
        with open(fileName,'w') as f: f.write(html)  
    else:
        raise Exception(u'下载页面异常')

def parse(question_path='/data/meiqiming/data/download/500004-数学/questions'):    
    fileNames = filter(lambda x: True if x.endswith('-700993') else False,os.listdir(question_path))
    with open('aaa.txt','w') as faaa:
        for fileName in fileNames:        
            questionId = fileName.split('-')[0]
            questionFileName = os.path.join(question_path,fileName)
            with open(questionFileName,'r') as f:
                html = f.read()         
            soup = BeautifulSoup(html,"lxml")
            scripts = soup.find_all(name ="script",attrs={'type':"text/javascript"}, text=re.compile("var\s*vo\s*=\s+(.+?)\s*;\s*with"))
            if not scripts: raise Exception(u"获取的网页状态不正常")
            vo_str = re.findall(r"var\s*vo\s*=\s*({.+?})\s*,\s*error\s*=",scripts[0].get_text())[0]
            try:
                vo = json.loads(vo_str)
            except Exception as ex:
                vo = json.loads(vo_str.replace('\t','\\t'))
            if str(vo['id']) != questionId:
                faaa.write(u'题目Id：%d,文件的名称%s\n'%(vo['id'],questionFileName))
            else:
                print vo['id'],questionFileName
def main(question_path='/data/meiqiming/data/download/500004-数学/questions'):    
    with open('repair.txt','r') as f:
        for fileName in f:
            downloadFile(fileName.replace('\n',''))

if __name__ == '__main__':
    #parse()
    main()
    
