#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from TikuSpider import TikuSpider
import re
import os
import sys
import logging
from k12_tiku_scrapy.settings import root_path,pic_path,tmp_suffix,start_urls
reload(sys)
sys.setdefaultencoding('utf8')

class TikuResumeSpider(TikuSpider):
    name = "k12_tiku_resume"

    def start_requests(self):
        urls = start_urls
        for url in urls:
            cid = re.findall(r'&cid=(.*?)$',url)[0]
            cn = re.findall(r'&cn=(.*?)&',url)[0]
            c_path = os.path.join(root_path, u'%s-%s/' %(cid,cn))
            knowed_path = c_path + 'knowled/'
            knowled_pg_path = c_path + 'knowled-pg/'
            questions_path = c_path + 'questions/'
            suffix = tmp_suffix            
            flag = True # 默认上级tmp文件不存在
            if flag:  
                #查找知识点是否有tmp文件      
                for konwed_tmp in self.getSuffixFiles(knowed_path,suffix):
                    flag = False
                    with open(konwed_tmp,'r') as f:                      
                        url = re.findall(r'url=(.+?)\s',f.read())[0]     
                    yield scrapy.Request(url=url,callback =self.parseKnowled) 
            if flag:
                print u'所有知识点已经下载完成'
                #查找知识点的分页的tmp文件
                for pg_tmp in self.getSuffixFiles(knowled_pg_path,suffix):
                    flag = False
                    print pg_tmp
                    with open(pg_tmp,'r') as f:
                        url = re.findall(r'url=(.+?)\s',f.read())[0]    
                    yield scrapy.Request(url=url,callback =self.parseKnowledPg)
            if flag:
                print u'所有知识点与其分页都已经下载完成'
                #查找题目的分页的tmp文件
                for question_tmp in self.getSuffixFiles(questions_path,suffix):
                    flag = False
                    with open(question_tmp,'r') as f:
                        url = re.findall(r'url=(.+?)\s',f.read())[0]    
                    yield scrapy.Request(url=url,callback =self.parseQuestion)
            if flag:
                print u'所有知识点、分页、题目都已经下载完成'
                #查找 图片的tmp文件
                for parent,dir_names,file_names in os.walk(pic_path):
                    for file_name in file_names:
                        if file_name.endswith(suffix):
                            flag = False     
                            file_g_name = os.path.join(parent,file_name)                     
                            with open(file_g_name,'r') as f:
                                url = re.findall(r'url=(.+?)\s',f.read())[0]
                            print parent,file_name,url   
                            yield scrapy.Request(url,callback=self.parseImg,meta={'file':file_g_name.rstrip(tmp_suffix)})
            if flag:
                print u'此次抓取的所有题目、图片已经完成，请重新启动k12_tiku进行验证'

    def getSuffixFiles(self,dir_path,suffix):
        return [ os.path.join(dir_path,file) for file in os.listdir(dir_path) if file.endswith(suffix)]
            