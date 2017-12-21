#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cfg import CFG
import threading
import Queue
import urllib
import time
import socket
import json
import LoggerUtil
import sys
reload(sys)
sys.setdefaultencoding('utf8')

logger = LoggerUtil.getLogger(__name__)
class IpPool(object):
    __max_interval = 12*60*60 #最大间隔重新获取Ip
    def __init__(self,proxys=CFG.PROXYS,maxIpNum=CFG.IP_NUM_MAX,minIpNum=CFG.IP_NUM_MIN,accessUrls=CFG.CHECK_URLS,delayTime=1.5):
       
        '''
        @proxys：格式如下map {'proxylists':{'url':'http://www.proxylists.net/cn_0_ext.html','method':getPorxyLists}} \n
        'method'代表处理url的方法
        '''
        self.__maxIpNum__ = maxIpNum
        self.__minIpNum__ = minIpNum
        self.__accessUrls__ = accessUrls
        self.__proxys__ = proxys
        self.__queue__ = Queue.Queue(maxIpNum) #存放验证后的代理IP的key
        self.__ip_map__= {} #用于代理IP排重
        self.__queue_crawl__ = Queue.Queue(maxIpNum) #存放爬取的代理IP信息
        self.__delay_time = delayTime #代理访问url最大允许延迟  
    def start(self):
        '''开启动态IP池'''
        #开启动态IP的爬取
        threading.Thread(target=self.__dynamic_crawl_ip,name="thread-crawl-ip").start()
        for i in range(2):  
            #处理已爬下来的代理
            threading.Thread(target=self.__handle_crawl_proxy,name=("handle-crawl-%d" % i)).start()
        for i in range(2):
            #开启IP有效性的过滤
            threading.Thread(target=self.__check_proxys,name=("check_proxys-%d" % i)).start()
        return self

    def __dynamic_crawl_ip(self):
        '''动态爬取Ip'''
        logger.info(u'开启动态爬取IP')
        begin = time.time()
        count = 1
        while True:
            qsize = self.getSize()
            interval = time.time() - begin
            flag = (qsize < self.__minIpNum__ ) or (interval > self.__max_interval)
            logger.info(u'查看是否满足重新爬取的条件:%r,已间隔时间:%f' % (flag,interval))
            if flag:
                logger.info(u'爬取网站IP-第%d次' % count)
                self.__spider_crawl_iP()
                begin = time.time()
                time.sleep(300)
                count += 1
            time.sleep(10) # 每隔10s检测一次是否需要重新爬取IP,根据网络情况设置循环的间隔时间（网络差时设置间隔短）
    def __spider_crawl_iP(self):
        '''爬取IP页面'''
        total = 0
        for key,proxy in self.__proxys__.items():
            count = 0  
            try:
                for proxy_address in proxy['method'](proxy['url']):  
                    self.__queue_crawl__.put(proxy_address)
                    logger.info(u'增加IP:%s,待处理IP数量%d' % (json.dumps(proxy_address),self.__queue_crawl__.qsize())) 
                    count += 1
                if  count == 0 :
                    logger.warn(u'爬取页面-编码:%s,url:%s,得到IP数量为0' %(key,proxy['url']))
                logger.info('完成页面%s的IP爬取',proxy['url'])
            except Exception as e:
                logger.error(u'爬取页面Ip重新异常,异常信息:%s' % e.message)
            total += count  
        logger.info(u'本次一共爬取IP数量:%d' %total)
    def __handle_crawl_proxy(self):
        '''处理已爬下来的代理'''
        logger.info(u'处理已爬下来的代理IP')
        socket.setdefaulttimeout(5) #设置5秒连接超时
        while True:
            proxy_address = self.__queue_crawl__.get()
            if self.check_proxy(proxy_address):                
                self.__putProxy(proxy_address)
            logger.info(u'处理IP:%s,待处理IP数量%d' % (json.dumps(proxy_address),self.__queue_crawl__.qsize())) 
    def __check_proxys(self):
        '''校验代理池的IP是否正常'''
        logger.info(u'校验代理池的IP是否正常')
        socket.setdefaulttimeout(5) #设置5秒连接超时
        while True:
            proxy_address = self.__popProxy()
            if self.check_proxy(proxy_address):                
                self.__putProxy(proxy_address)
            logger.info(u'有效Ip数量%d' % self.getSize())
            time.sleep(5) # 每隔5秒检测一个Ip
    
    def __putProxy(self,proxy_address):
        address = '%s:%s' %(proxy_address['ip'],proxy_address['port'])
        if self.__ip_map__.has_key(address):
            pass
        else:
            self.__queue__.put(address)
            self.__ip_map__[address]= proxy_address
    def __popProxy(self):
        address = self.__queue__.get()
        proxy_address = self.__ip_map__.pop(address)
        return proxy_address

    def getProxyIp(self):
        '''获取IP'''
        proxy_address =  self.__popProxy()
        self.__putProxy(proxy_address)
        return proxy_address
    def getSize(self):
        return self.__queue__.qsize()

    def check_proxy(self,proxy_address):
        proxies = "http://%s:%s" % (proxy_address['ip'], proxy_address['port'])
        for url in self.__accessUrls__:      
            try:
                begin = time.time()
                urllib.urlopen(url, proxies={'http': proxies}) 
                rep_time = time.time()-begin
                if  rep_time > self.__delay_time:
                    logger.warn(u'代理(%s)请求超过最大时间,响应时间:%f,允许最大延迟时间:%f' %(proxies,rep_time,self.__delay_time))
                    return False
                time.sleep(0.1) #连续访问容易出现异常
            except Exception as e:
                logger.warn(u'代理(%s),校验出现异常:%s',proxies,e.message)
                return False
        return True          

#if __name__ == '__main__':
#    ips = IpPool().start()
    