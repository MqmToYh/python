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
from TikuSpider import TikuSpider
from k12_tiku_scrapy.settings import root_path,pic_path,tmp_suffix,start_urls
reload(sys)  
sys.setdefaultencoding('utf8')
fileCodeing = sys.getfilesystemencoding()
#html转义字符处理
html_parser = HTMLParser.HTMLParser()

#html_file = '/data/meiqiming/htmls/history.middle.html'
html_file = 'htmls/history.middle.html'
class TikuThreeSpider(TikuSpider):
    name = "k12_tiku_three"
    def start_requests(self):
        with open(html_file,'r') as f:
            soup = BeautifulSoup(html_parser.unescape(f.read()),"lxml")
        cid_path = None
        for f_soup in soup.find_all('li',{"class":"tree-node tree-node-0 z-open"}):
            f_url = f_soup.a['href']
            if cid_path is None:
                cid = re.findall(r'&cid=(.*?)&',f_url)[0]
                cn = re.findall(r'&cn=(.*?)&',f_url)[0]
                cn = urllib2.unquote(cn).decode()
                cid_path = os.path.join(root_path, '%s-%s/knowled/' % (cid,cn))
                if not os.path.exists(cid_path):
                    os.makedirs(cid_path)
            for second_selector in f_soup.find_all('dl',{"class": "z-open"}):           
                for third_selector in second_selector.find_all('dd', {"class": "tree-node-2"}):
                    fid = third_selector.a["data-ftid"]
                    first_title = f_soup.a["title"]
                    sid = third_selector.a["data-sid"]
                    second_title = second_selector.dt.a["title"]
                    tid = third_selector.a["data-id"]
                    third_title = third_selector.a["title"]                        
                    #创建临时文件
                    t_url = f_url + '&sdid=%s&tdid=%s' %(sid,tid)
                    knowled_file = os.path.join(cid_path,'%s-%s-%s-download' %(fid,sid,tid))                    
                    #print first_title,fid,second_title,sid,third_title,tid,t_url   
                    if not os.path.exists(knowled_file):
                        with open(knowled_file+tmp_suffix,'wb') as f: f.write('url=%s\n' % t_url)
                        yield scrapy.Request(t_url,callback=self.parseThreeKnowled)
                    else:
                        #页面存在就直接获取count
                        with open(knowled_file,'r') as f: 
                            text = f.read()
                            count = int(re.findall(r'count=(\d+?)\s',text)[0])                
                        print 'knowled_three_file:%s - exists' % knowled_file
                        for pg_scrapy  in self.getKnowlePgScrapy(t_url,count,fid,cid,cn,tid):
                            yield pg_scrapy  

    def parseThreeKnowled(self,response):  
        print 'parseThreeKnowled',response.url
        #解析文档，获取知识点下题目数量
        count = response.xpath('.//div[@class="g-mn"]/ul/li[@class="filter"]/span/strong/text()').extract()[0]
        count = int(count)
        cid = re.findall(r'&cid=(.*?)&',response.url)[0]
        cn = re.findall(r'&cn=(.*?)&',response.url)[0]
        cn = urllib2.unquote(cn).decode()
        ftid = re.findall(r'&ftid=(.*?)&',response.url)[0]
        sdid = re.findall(r'&sdid=(.*?)&',response.url)[0]
        tdid = re.findall(r'&tdid=(.*?)$',response.url)[0]
        knowled_file = os.path.join(root_path,'%s-%s/knowled/%s-%s-%s-download'  % (cid,cn,ftid,sdid,tdid))
        shutil.move(knowled_file+tmp_suffix,knowled_file)
        with open(knowled_file,'ab') as f:f.write('count=%d\n' % count)        
        for pg_scrapy  in self.getKnowlePgScrapy(response.url,count,ftid,cid,cn,tdid):
            yield pg_scrapy
    
    #重写分析分页的代码
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
        tdid = re.findall(r'&tdid=(.*?)&',response.url)[0]
        page = re.findall(r'&page=(.*?)&',response.url)[0]
        #修改文件名称，确认此文件已经下载
        pg_file = root_path + '%s-%s/knowled-pg/%s-pg-%s' %(cid,cn,tdid,page)
        shutil.move(pg_file+tmp_suffix,pg_file)
        #保存pg页面
        with open(pg_file,'wb') as f:f.writelines(response.body)
        #保存题目的根目录
        q_path = root_path + '%s-%s/questions/' %(cid,cn)        
        #解析文档
        question_hrefs=response.xpath('.//div[@class="g-mn"]/ul[@class="m-list"]/li[@class="question-box"]/div/div/a[@class="u-btn"]/@href').extract()
        for q_scrapy in self.getQuestionScrapy(question_hrefs,response.url,q_path,ftid):
            yield q_scrapy          


