#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import requests
import HTMLParser
import urllib2
from bs4 import BeautifulSoup
import urlparse
import time
import LoggerUtil
import sys
reload(sys)
sys.setdefaultencoding('utf8')

logger = LoggerUtil.getLogger(__name__)
#html转义字符处理
html_parser = HTMLParser.HTMLParser()

def getPorxyLists(url,recursion=True):
    '''proxylists的网页的ip代理'''
    try:
        logger.info(u'开始请求url:%s' %url)
        response = requests.get(url,timeout=5)
        logger.info(u'返回url:%s的内容' %url)
        html_soup = BeautifulSoup(html_parser.unescape(response.content),'lxml')
        tr_tags= html_soup.find_all('table',{'style':True})[0].find_all('tr')
        for tr_soup in tr_tags[2:-1]:
            td_tags = tr_soup.find_all('td')
            ip_info = re.findall(u'unescape\(\'(.+?)\'\)',td_tags[0].get_text())[0]
            ip = re.findall(u'writeln\("(.+?)"\)',urllib2.unquote(ip_info))[0]
            port = td_tags[1].get_text().strip()
            checkedTime = td_tags[-1].get_text().strip()
            yield {'ip':ip,'port':port,'checkedTime':checkedTime} 
        if recursion:
            a_tags = tr_tags[-1].find_all('a')
            for a in a_tags:
                new_url = urlparse.urljoin(url,a['href'])
                if url != new_url:
                    time.sleep(0.1) #连续访问容易出现异常
                    for proxy_address in getPorxyLists(new_url,False):
                        yield proxy_address
    except Exception as e:
        logger.error('proxylists的网页的ip代理处理异常，url:%s ,错误信息:%s' %(url,e.message))


      

if __name__ == '__main__':
    #%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())
    #for proxy_address in getPorxyLists('http://www.proxylists.net/cn_0_ext.html'):
    #    print proxy_address
    pass
       
