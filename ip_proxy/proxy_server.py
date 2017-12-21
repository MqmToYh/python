#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from SocketServer import ThreadingMixIn 
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler 
import threading
import time
from cfg import CFG
from ip_pool import IpPool
import LoggerUtil
import sys
reload(sys)
sys.setdefaultencoding('utf8')
logger = LoggerUtil.getLogger(__name__)

ipPool = IpPool()
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):     
        address = ipPool.getProxyIp()
        message = json.dumps(address)
        logger.info(u'get 请求获取IP--%s' % message)
        #logger.info(u"ip total:%d" % ipPool.getSize())        
        #self.send_response(200)
        #self.send_header('Content-type','text/html')
        #self.send_header('Uri',self.path)
        #self.end_headers()
        self.wfile.write(message)
class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass

def main():  
    ipPool.start()
    server_address = (CFG.ADDRESS,CFG.PORT)
    server = ThreadingHttpServer(server_address, MyHandler)
    server.serve_forever()
    
if __name__ == '__main__':
    main()