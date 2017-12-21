#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import threading
import sys
reload(sys)  
sys.setdefaultencoding('utf8')


if __name__=="__main__":
    print u'开启主k12_tiku爬虫'
    os.system('scrapy crawl k12_tiku')  
    for t in threading.enumerate():
        if t is threading.currentThread():
            continue
        t.join() 

    for i in range(1,3):
        print u'开启 k12_tiku_resume第%d次' % i
        os.system('scrapy crawl k12_tiku_resume ')    
        for t in threading.enumerate():
            if t is threading.currentThread():
                continue
            t.join()