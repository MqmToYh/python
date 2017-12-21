#!/usr/bin/env python
# -*- coding: utf-8 -*-
from parse_proxy_html import *

class CFG(object):
    ADDRESS=''
    PORT=8089
    PROXYS={
        'proxylists':{'url':'http://www.proxylists.net/cn_0_ext.html','method':getPorxyLists}
    }
    IP_NUM_MAX=1000
    IP_NUM_MIN=50
    CHECK_URLS = ["http://www.baidu.com",]

