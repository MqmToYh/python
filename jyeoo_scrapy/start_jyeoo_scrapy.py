#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import threading
import sys
reload(sys)  
sys.setdefaultencoding('utf8')


if __name__=="__main__":
    for i in range(1,3):
        print u'开启主jyeoo_image爬虫第%d次' % i
        os.system('scrapy crawl jyeoo_image')  
        for t in threading.enumerate():
            if t is threading.currentThread():
                continue
            t.join()
