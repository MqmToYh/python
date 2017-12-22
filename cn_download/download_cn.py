#!/usr/bin/env python
# -*- coding:utf-8 -*-
from multiprocessing.pool import ThreadPool
import HTMLParser #处理html编码字符
from bs4 import BeautifulSoup #lxml解析器
import urllib2 #url 请求
import urllib 
import re #正则
import json #json
from SqlUtil import Mysql,PostgreSql
from cfg import PATH,SQL,URLS
import LoggerUtil
import urlparse
import os
import cgi
import socket
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver import DesiredCapabilities
import sys #设置系统属性
reload(sys)  
sys.setdefaultencoding('utf8')

socket.setdefaulttimeout(20)
logger = LoggerUtil.getLogger(__name__)
logger_cn = LoggerUtil.getCnLogger()
htmlParser = HTMLParser.HTMLParser()

def initdir(init_paths =(PATH.html_path,PATH.pic_path,PATH.voice_path,PATH.html_zdic_path)):
    '''初始化目录'''
    for init_path in init_paths:
        if not os.path.exists(init_path) : os.makedirs(init_path)

def downloadHanyu(cn,html_path=PATH.html_path, url=URLS.cn_url):
    try:
        html_file = os.path.join(html_path,u"%s-cn.html"%cn)
        if os.path.exists(html_file):
            with open(html_file,'r') as f: html = f.read() 
        else:
            req=urllib2.Request(url % cn)
            req.add_header('Accept-Language','zh-CN,zh;q=0.8')
            req.add_header('Host','hanyu.baidu.com')
            req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36")
            html = urllib2.urlopen(req).read() 
            with open(html_file,'w') as f: f.write(html)  
        zdic_soup = BeautifulSoup(htmlParser.unescape(downloadZdic(cn)),"lxml")
        h_zdic_soup = zdic_soup.find('table',attrs={'id':'z_info'})
        #字形
        font = h_zdic_soup.find('center').a.get_text()     
        if font:
            font = font.replace(u'结构','')
        cn_soup = BeautifulSoup(htmlParser.unescape(html),"lxml").find('div',attrs={'id':'word-body'})
        h_soup = cn_soup.find('div',attrs={'id':'word-header'})
        img = h_soup.find('img',attrs={'id':'word_bishun'})
        if img:
            img_url= img['data-gif']
            #笔顺图片
            picture = downloadImg(img_url)
        else: picture = None     
        #拼音
        #pinyin = []
        #语音
        #voice= []
        #for span in h_soup.find('div',attrs={'id':'pinyin'}).find_all('span'):
            #pinyin.append(span.b.get_text())
            #voice.append(downloadVoice(span.a['url']))
        #部首
        radical = h_soup.find('li',attrs={'id':'radical'}).span.get_text()
        #笔画
        strokes = int(h_soup.find('li',attrs={'id':'stroke_count'}).span.get_text())
        #繁体
        tra_soup = h_soup.find('li',attrs={'id':'traditional'})   
        traditional = tra_soup.span.get_text() if tra_soup else None        
        #五行
        wuxing_soup = h_soup.find('li',attrs={'id':'wuxing'})    
        wuxing = wuxing_soup.span.get_text() if wuxing_soup else None
        #五笔
        wubi_soup = h_soup.find('li',attrs={'id':'wubi'})    
        wubi = wubi_soup.span.get_text() if wubi_soup else None
        if not wubi:           
            tr_soup =  zdic_soup.find('table',attrs={'id':'z_info2'}).find_all('tr')
            try:
                if tr_soup[0].find_all('td')[1].span['id'] == 'z_i_t3_wb_l':           
                    wubi = tr_soup[1].find_all('td')[1].span.get_text()              
            except Exception as e:
                logger.error(e.message)
        #定义
        definition =re.findall(u'\"definition\"\s*:\s*\"(.+?)\"\s*}\s*;',h_soup.find('script').get_text())[0].decode('unicode_escape')
        #基本意思
        basicmean = cn_soup.find('div',attrs={'id':'basicmean-wrapper'}).find(attrs={'class':'tab-content'}).decode()
        #详细的意思
        de_soup = cn_soup.find('div',attrs={'id':'detailmean-wrapper'})
        detailmean = de_soup.find(attrs={'class':'tab-content'}).decode() if de_soup else None
        
        # 以此结构组织[{"code":"luo1","pinyin":"luō","vocie":"luo1.mp3","paraphrase":"见「啰唆」。"}]
        pinyin_info = []
        dl_soup = cn_soup.find('div',attrs={'id':'basicmean-wrapper'}).find(attrs={'class':'tab-content'}).find_all('dl')
        pin_details =definition.split("||")
        i = 0
        for span in h_soup.find('div',attrs={'id':'pinyin'}).find_all('span'):
            info = {}
            pin_detail = pin_details[i].split("#")  
            info['pinyin'] = span.b.get_text()  
            if pin_detail[0] !=  info['pinyin']:
                raise Exception(u'文本解析与拼音无法对应')
            info['code'] = pin_detail[1]
            info['definition'] = pin_detail[2]            
            info['vocie'] = downloadVoice(span.a['url'])

            paraphrase = dl_soup[i].decode()
            if dl_soup[i].dt: paraphrase = paraphrase.replace(dl_soup[i].dt.decode(),'')
            if len(dl_soup) > 1 and dl_soup[i].dt.get_text().find(info['pinyin']) == -1:
                raise Exception(u'html解析与拼音无法对应')                
            else:
                info['paraphrase'] = cgi.escape(paraphrase.replace('\n',''))
            pinyin_info.append(info)
            i +=1
        
        if cn == '适':
            definition = None
            basicmean = None
            pinyin_info[1]['paraphrase'] = None
            pinyin_info[1]['definition'] = None
        return (cn,picture,json.dumps(pinyin_info,ensure_ascii=False),radical,strokes,traditional,wuxing,wubi,font,definition,basicmean,detailmean)
        #return (cn,picture,json.dumps(pinyin,ensure_ascii=False),json.dumps(voice,ensure_ascii=False),radical,strokes,traditional,wuxing,wubi,font,definition,basicmean,detailmean)
    except Exception as e:
        logger_cn.info(cn)
        logger.exception(u'处理汉字:%s,错误信息：%s' % (cn,e.message))
        return None
    
def downloadImg(url,pic_path=PATH.pic_path):    
    return downloadFile(url,pic_path,'img')
def downloadVoice(url,voice_path=PATH.voice_path):
    return downloadFile(url,voice_path,'voice')

def downloadFile(url,save_path,fileType='file'):
    url_path = urlparse.urlsplit(url)  
    file_name =os.path.join(save_path,url_path.path[1:])
    rs = url_path.path if fileType != 'voice' else os.path.basename(file_name)
    if not os.path.exists(file_name):
        try:
            html = getHtml(url) 
        except Exception as e:
            if fileType == 'voice':
                html = getHtml('http://www.zdic.net/p/mp3/' + rs)
            else:
                raise e
        with open(file_name,'wb') as f: f.write(html)
    return rs
def getHtml(url):
    req=urllib2.Request(url)
    req.add_header('Accept-Language','zh-CN,zh;q=0.8')
    req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36")
    return urllib2.urlopen(req).read()

def batchDownloadHanyu(cns,mysql,insert_sql=SQL.insert_sql):
    rs = map(downloadHanyu,cns)
    params = filter(lambda x: True if x else False , rs)
    if params:
        try:
            mysql.batchExecute(insert_sql,params)
            mysql.commit()
            return len(params)
        except Exception as e:
            mysql.rollback()
            logger.exception('执行SQL失败，失败原因%s'%e.message)
            return 0

def main(cn_file=PATH.cn_file):
    initdir()
    cns = []
    total = 0
    sucess_count = 0
    postgre = PostgreSql()
    try:
        with open(cn_file,'r') as f:        
            for line in f:
                cn = unicode(line)[0]
                if cn == '#': continue
                total += 1                
                cns.append(cn)
                if total % 50 == 0:
                    sucess_count +=batchDownloadHanyu(cns,postgre)
                    cns = []
                    print u'一共处理汉字%d,成功处理汉字%d,处理失败的汉字%d' %(total,sucess_count,total-sucess_count)
        if cns:
            sucess_count += batchDownloadHanyu(cns,postgre)
            print u'一共处理汉字%d,成功处理汉字%d,处理失败的汉字%d' %(total,sucess_count,total-sucess_count)
    finally:
        postgre.close()
def downloadZdic(cn,html_path=PATH.html_zdic_path):
    try:
        fileName = os.path.join(html_path,'%s_zdic' % cn)
        if os.path.exists(fileName):
            with open(fileName,'r') as f: html_text = f.read() 
            if html_text:      
                return html_text
        url = 'http://www.zdic.net/sousuo/'
        req=urllib2.Request(url)
        req.add_header('Host','www.zdic.net')
        req.add_header('Content-Type','application/x-www-form-urlencoded')
        req.add_header('Accept-Language','zh-CN,zh;q=0.8')
        req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36")
        data = {'lb_a':'hp','lb_b':'mh','lb_c':'mh','tp':'tp1','q':cn}
        rep = urllib2.urlopen(req,urllib.urlencode(data))
        html = rep.read() 
        title = BeautifulSoup(htmlParser.unescape(html),"lxml").find('title').get_text()
        assert '%s的解释|%s的意思|汉典“%s”字的基本解释' % (cn,cn,cn) in title
        with open(fileName,'w') as f: f.write(html)
        with open(html_path+"cn_url.txt",'a') as f: f.write('%s  %s\n'%(cn, rep.url))
        return html
    except Exception as e:
        logger.exception('%s-处理是出错，错误信息:%s'%(cn,e.message))
        return None
def downloadZdicAll(cn_file=PATH.cn_file):
    initdir()
    pool = ThreadPool(100)
    count = 0
    with open(cn_file,'r') as f:        
        for line in f:
            cn = unicode(line)[0]
            if cn == '#': continue
            count +=1
            pool.apply_async(downloadZdic,cn)
            if count % 100 == 0:
                print u'已加载汉字数量%d'% count
    pool.close()
    pool.join()

#潾-没有图片 Ｑ-舍弃
if __name__ == '__main__':   
    #downloadZdicAll()
    main()
    #mysql = Mysql()
    #batchDownloadHanyu([u'适'],mysql)
    #mysql.close()
    #print '𨓈'
    #print '\ud861\udcc8'.decode('unicode_escape').encode('utf-8')