#!/usr/bin/env python
#-*-coding:utf-8-*-

import scrapy
import re
import urllib2
from bs4 import BeautifulSoup
from k12_tiku_scrapy.items import KnowledItem
import os 
import shutil #移动文件
import json
import sys
import HTMLParser
import urlparse
import time
import logging
from k12_tiku_scrapy.settings import root_path,pic_path,tmp_suffix,start_urls
reload(sys)  
sys.setdefaultencoding('utf8')
fileCodeing = sys.getfilesystemencoding()
#html转义字符处理
html_parser = HTMLParser.HTMLParser()

baseUrl = 'http://k12.tiku.com/'
class TikuSpider(scrapy.Spider):
    name = "k12_tiku"
    def start_requests(self):
        urls = start_urls
        for url in urls:
            yield scrapy.Request(url=baseUrl+url, callback=self.parse)

    def parse(self,response):  
        print 'parse',response.url 
        axs = response.xpath('.//ul[@class="m-tree"]/li[contains(@class,"tree-node")]/a')
        cid = re.findall(r'&cid=(.*?)$',response.url)[0]
        cn = re.findall(r'&cn=(.*?)&',response.url)[0]
        cn = urllib2.unquote(cn).decode()
        cid_path = root_path + '%s-%s/knowled/' % (cid,cn)
        if not os.path.exists(cid_path):
            os.makedirs(cid_path)     
        for a in axs:
            url = response.urljoin(a.xpath('./@href').extract()[0])
            knowledId = re.findall('&ftid=(.*?)&',url)[0]
            KnowledName = a.xpath('./@title').extract()[0]
            #item = {'url':url,'cid':cid,'KnowledId':KnowledId,'KnowledName':KnowledName}
            knowled_file = cid_path + '%s-download' % knowledId
            if not os.path.exists(knowled_file):
                with open(knowled_file+tmp_suffix,'wb') as f: f.write('url=%s\n' % url)
                yield scrapy.Request(url=url,callback =self.parseKnowled)
            else:
                #页面存在就直接获取count
                with open(knowled_file,'r') as f: 
                    text = f.read()
                    count = int(re.findall(r'count=(\d+?)\s',text)[0])                
                print 'knowled_file:%s - exists' % knowled_file
                for pg_scrapy  in self.getKnowlePgScrapy(url,count,knowledId,cid,cn):
                    yield pg_scrapy    
    def parseKnowled(self,response):
        print 'parseKnowled',response.url
        #解析文档，获取知识点下题目数量
        count = response.xpath('.//div[@class="g-mn"]/ul/li[@class="filter"]/span/strong/text()').extract()[0]
        count = int(count)
        #获取必要的信息
        cid = re.findall(r'&cid=(.*?)&',response.url)[0]
        cn = re.findall(r'&cn=(.*?)&',response.url)[0]
        cn = urllib2.unquote(cn).decode()
        ftid = re.findall(r'&ftid=(.*?)&',response.url)[0]
        #修改文件名称，确认此文件已经下载
        knowled_file = root_path + '%s-%s/knowled/%s-download'  % (cid,cn,ftid)
        shutil.move(knowled_file+tmp_suffix,knowled_file)
        with open(knowled_file,'ab') as f:f.write('count=%d\n' % count)        
        for pg_scrapy  in self.getKnowlePgScrapy(response.url,count,ftid,cid,cn):
            yield pg_scrapy

    def getKnowlePgScrapy(self, parentUrl,count,ftid,cid,cn,tdid=None):
        '''获取开始知识点分页面爬取'''
        pg_path = root_path + '%s-%s/knowled-pg/' %(cid,cn)
        if not os.path.exists(pg_path):
            os.makedirs(pg_path)
        rows = 1000
        if count > 0:
            #生成pg
            pages = count/rows + (1 if count % rows else 0)
            for page in range(1, pages+1):
                try:
                    url = parentUrl+'&page=%d&rows=%d' % (page,rows)
                    pg_file = pg_path+'%s-pg-%d' %(tdid if tdid else ftid,page)
                    if not os.path.exists(pg_file):
                        with open(pg_file+tmp_suffix,'wb') as f : f.write('url=%s\n' % url)
                        yield scrapy.Request(url=url,callback=self.parseKnowledPg) 
                    else:
                        print 'pg_file:%s - exists' % pg_file
                        with open(pg_file,'r') as f:
                            text = f.read()
                        pg_soup = BeautifulSoup(html_parser.unescape(text),"lxml")
                        #解析文档
                        question_hrefs= [ a['href'] for a in  pg_soup.find("ul",{"class":"m-list"}).find_all('a',{"class":"u-btn"}) ]
                        q_path = root_path + '%s-%s/questions/' %(cid,cn)
                        for q_scrapy in self.getQuestionScrapy(question_hrefs,url,q_path,ftid):
                            yield q_scrapy  
                except Exception as ex:
                    logging.exception(u'处理url:%s的第%d分页异常,错误信息:%s'%(parentUrl,page,ex.message))        

    def parseKnowledPg(self,response):    
        print 'parseKnowledPg',response.url
        #确认页面题目数量不为0
        count = response.xpath('.//div[@class="g-mn"]/ul/li[@class="filter"]/span/strong/text()').extract()[0]
        if count == '0': raise Exception(u'分页页面题目数量为0异常')        
        #获取必要的信息
        cid = re.findall(r'&cid=(.*?)&',response.url)[0]
        cn = re.findall(r'&cn=(.*?)&',response.url)[0]
        cn = urllib2.unquote(cn).decode()
        ftid = re.findall(r'&ftid=(.*?)&',response.url)[0]
        page = re.findall(r'&page=(.*?)&',response.url)[0]
        #修改文件名称，确认此文件已经下载
        pg_file = root_path + '%s-%s/knowled-pg/%s-pg-%s' %(cid,cn,ftid,page)
        shutil.move(pg_file+tmp_suffix,pg_file)
        #保存pg页面
        with open(pg_file,'wb') as f:f.writelines(response.body)
        #保存题目的根目录
        q_path = root_path + '%s-%s/questions/' %(cid,cn)        
        #解析文档
        question_hrefs=response.xpath('.//div[@class="g-mn"]/ul[@class="m-list"]/li[@class="question-box"]/div/div/a[@class="u-btn"]/@href').extract()
        for q_scrapy in self.getQuestionScrapy(question_hrefs,response.url,q_path,ftid):
            yield q_scrapy          

    def getQuestionScrapy(self,question_hrefs,pg_url,q_path,ftid):
        #print u'question_hrefs 数量:%s' %len(question_hrefs)           
        if not os.path.exists(q_path):
            os.makedirs(q_path)
        for href in question_hrefs:
            try:
                questionId = re.findall(r'&id=(.*?)&',href)[0]
                question_url = urlparse.urljoin(pg_url,href)
                question_file = q_path + ('%s-%s' % (questionId,ftid))
                if not os.path.exists(question_file):
                    with open(question_file+tmp_suffix,'wb') as qf: qf.write('url=%s\n'% question_url)
                    yield scrapy.Request(url=question_url,callback=self.parseQuestion)
                else:
                    #查看图片是否已经下载完成,未下载完就开启下载
                    #print 'question_file:%s - exists' % question_file
                    with open(question_file,'r') as f:
                        text = f.read()
                    q_soup = BeautifulSoup(text,"lxml")
                    scripts = q_soup.find_all(name ="script",attrs={'type':"text/javascript"}, text=re.compile("var\s*vo\s*=\s+(.+?)\s*;\s*with"))
                    vo_strs = re.findall(r"var\s*vo\s*=\s*({.+?})s*,\s*error\s*=",scripts[0].get_text())  
                    try:
                        vo = json.loads(vo_strs[0])
                    except Exception as ex:
                        vo = json.loads(vo_strs[0].replace('\t','\\t'))
                    try:
                        for i_scrapy in self.getImgScrapy(vo):
                            yield i_scrapy
                    except Exception as ex:
                        logging.exception(u'处理文件名称为:%s，的ImgScrapy方法异常,异常信息:%s' %(question_file,ex.message))
            except Exception as e:
                logging.exception(u'处理题目Question_url:%s,错误信息:%s'%(href,e.message))
    def parseQuestion(self,response):        
        print 'parseQuestion',response.url     
        #获取必要的信息
        cid = re.findall(r'&courseId=(.*?)$',response.url)[0]
        cn = re.findall(r'&cn=(.*?)&',response.url)[0]
        cn = urllib2.unquote(cn).decode()
        qid = re.findall(r'&id=(.*?)&',response.url)[0]
        #解析
        for script in response.xpath('.//script/text()'):
            vo_strs = re.findall(r"var\s*vo\s*=\s*({.+?})s*,\s*error\s*=",script.extract())            
            if vo_strs:  
                try:
                    vo = json.loads(vo_strs[0])
                except Exception as ex:
                    vo = json.loads(vo_strs[0].replace('\t','\\t'))
                ftid = vo['firstKnowledgeId']
                #确认下载页面正确,并保存下载页面
                question_file = root_path + '%s-%s/questions/%s-%s' %(cid,cn,qid,ftid)
                shutil.move(question_file+tmp_suffix,question_file)
                with open(question_file,'wb') as f:f.writelines(response.body)
                try:
                    for i_scrapy in self.getImgScrapy(vo):
                        yield i_scrapy
                except Exception as e:
                    logging.exception(u'处理文件名称为:%s，的ImgScrapy方法异常,异常信息:%s' %(question_file,e.message))
                
        #time.sleep(3)
    def getImgScrapy(self,vo): 
        #生成下载图片的url
        img_urls=[]
        for a_html in [vo['answerHtml'],vo['anylysisHtml'],vo['bodyHtml'],vo['optionHtmlList'] if 'optionHtmlList' in vo else '']:
            i_soup = BeautifulSoup(html_parser.unescape(a_html),"lxml")
            img_urls.extend([ img['src'] for img in i_soup.find_all('img') if img.has_attr('src')])
        #下载图片
        for img_url in img_urls:  
            try:               
                #解析图片下载路径地址不正确
                img_url = re.sub('([^:])//', '\g<1>/', img_url)   
                fileName = re.findall(r'https?://.+?/(.+)$',img_url)
                if not fileName:
                    messge = u'图片地址格式不正确-cid:%s,questionId:%s,src:%s' % (vo['courseId'],vo['id'],img_url)
                    logging.error(messge)
                    continue  
                file = pic_path + fileName[0]
                dirname = os.path.dirname(file)
                if not os.path.exists(file):
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                    with open(file+tmp_suffix,'wb') as f: f.write('url=%s\n' % img_url)
                    #执行下载图片
                    if img_url == 'http://tikucommon-zs.oss-cn-beijing.aliyuncs.com/tiku/source/tikupic//4d/4d/4db4df53a6f395fc289415dd44c6ff9e.jpg':
                        print 'img_url',vo['id']
                    yield scrapy.Request(url=img_url,callback=self.parseImg,meta={'file':file})
            except Exception as ex:
                logging.exception(u'题目id:%s-%s,处理图片url:%s异常,错误信息:%s' %(vo['id'],vo['courseId'],img_url,ex.message))
    def parseImg(self,response):
        print 'parseImg',response.url
        if response.status in [404]:
            pass
        else:
            file = response.meta['file']
            shutil.move(file+tmp_suffix,file)
            with open(file,'wb') as f:f.writelines(response.body)
