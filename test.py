#!/usr/bin/python
#-*-coding:utf-8-*-

import threading #线程处理
import time
import cgi  
import HTMLParser
from bs4 import BeautifulSoup
import re
import json
import Queue
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
#html转义字符处理
html_parser = HTMLParser.HTMLParser()
     
'''
yield 一步步执行
def fib(max):  
    a = 1   
    print "aaaa" 
    while a < max: 
        yield {"a%d" % a : a}
        a+=1

       
  
m = fib(12)
print m
print "2222"
for i in m:
    print i

print m.next()  
print m.next()  
print m.next() 
print m.next() 
'''

'''
class SemaphoreThread(threading.Thread):
    """控制同步处理的线程数量"""
   
    def __init__(self,threadName,semaphore):
        """initialize thread"""       
        threading.Thread.__init__(self,name=threadName)
        self.semaphore=semaphore

    def run(self):
        """Print message and release semaphore"""    
        self.semaphore.acquire()
        print "%s semaphore %s.\n" % (self.getName(),"start")
        time.sleep(5)
        #free a table
        print " %s semaphore  %s.\n" % (self.getName(),"end")
        self.semaphore.release()

threads=[]
sem = threading.Semaphore(1)
for i in range(1,11):
    t = SemaphoreThread("thread"+str(i),sem)
    t.start()
'''

def startStr(*startstrs):
    '''
    返回一个检验字符串是否已规定字符开始的函数 \n
    startstring:设置规定的开始字符串（可以是多个，只要满足之一就可以）    
    '''
    def run(s):     
        '''
        返回True或None \n
        s：待检验的字符串 \n
        s以规定字符串开始返回True，否则返回false
        '''  
        f = map(s.startswith,startstrs)
        if True in f: return s
    return run

def testFilter():
    startM = startStr("4567","123")
    s = ["1234567","34561234567","4567897","2345434567897"]
    ss = filter(startM,s)
    print ss

def testHtmlecscape():
    s1 = "Hello <strong>world</strong>"
    s2 = cgi.escape(s1)  
    print  s2
    html_parser = HTMLParser.HTMLParser()
    txt = html_parser.unescape(s2)
    print s1

def testReMatch():
    if re.match("^A$|B$|C$|D$","D"):
        print 'True'
    else:
        print 'Flase'
def testJson():
    data=[{u'\u663e\u793a': [u'python', u'\u8bd5\u9a8c'], u'\u6570\u91cf': 22, u'\u8bed\u8a00': u'python'}]  
    data_c = u'\u663e\u793a'  
    print data  
    print data_c      
    res_data=json.dumps(data,ensure_ascii=False,encoding="gb2312")  
    print res_data   
def testReSubFindall():
    url = 'http://tikucommon-zs.oss-cn-beijing.aliyuncs.com/tiku/source/tikupic//4d/4d/4db4df53a6f395fc289415dd44c6ff9e.jpg'
    out = re.sub('([^:])//', '\g<1>/', url)
    print url
    print out

    a_html= u"&lt;p&gt;（1）答案见图（2分）&lt;/p&gt;&lt;p&gt;&lt;img width=&quot;396&quot; height=&quot;300&quot; &gt;&lt;/p&gt;&lt;p&gt;（2）①内蒙古，呼和浩特（2分）   ②鄂，武汉（2分）    ③青，西宁（2分）&lt;/p&gt;&lt;p&gt;（3）a海南省（1.5分），b新疆维吾尔自治区（1.5分）&lt;/p&gt;&lt;p&gt;（4）答案见图（2分）&lt;/p&gt;&lt;p&gt;（5）A西藏自治区（2分）   B广西壮族自治区（2分）&lt;/p&gt;"
    #a_html =u"&lt;span class&gt;&lt;/span&gt;读图填空&lt;br&gt;（1）A：______湾B：______洋G：______海&lt;br&gt;N：______  运河&lt;br&gt;（2）E：______河流F：______岛屿&lt;br&gt;（3）C是______沙漠，该地是______气候D是______盆地&lt;br&gt;该地是______气候．&lt;br&gt;（4）M 地的居民是______人种，他们的信奉______教．&lt;br&gt;&lt;br&gt;&lt;img src=&quot;http://tikucommon-zs.oss-cn-beijing.aliyuncs.com/tiku/source/upimg/czdl/STSource/20131101155836171380223/SYS201311011558361713802027_ST/images0.png&quot; &gt;"
    i_soup = BeautifulSoup(html_parser.unescape(a_html),"lxml")
    img_urls = []    
    img_urls.extend([ img['src'] for img in i_soup.find_all('img') if img.has_attr('src')])    
    print img_urls
    pic_path = 'data/pic/'
    img_url = u'http:///D:/最新客户端/temppic/Imagen129806564541562500.png'
    img_url = re.sub(u'([^:])//', '\g<1>/', img_url) 
    filename = re.findall(u'https?://.+?/(.+)$',img_url)
    if not filename :
        print 'not filename '
    else:
        file = pic_path + filename[0]
        print img_url,file

def testQueue():
    queue = Queue.Queue(30) 
    for i in range(30):
        queue.put(i)
    while True:        
        print queue.qsize(),queue.get()
def testDic():
    userDic={'0001':'maxianglin','0002':'wanglili','0003':'malinlin'}  
    print userDic.has_key('0004')  
    print userDic.has_key('0002')
    #a = userDic['0002']  
    #del userDic['0002']
    a =userDic.pop('0002')
    print a
    print userDic.has_key('0002')

quequ_ = Queue.Queue(3)
quequ_.put(1)
quequ_.put(2)
quequ_.put(3)
def testTime():
    begin = time.time()
    count = 1
    while True:
        time.sleep(2)
        end = time.time()
        print u"111-sleep %fs,第%d次\n,quequ:%s" % (end - begin,count,quequ_.qsize())
        begin = end
        quequ_.get()
        count += 1
def testTime2():
    begin = time.time()
    count = 1
    while True:
        time.sleep(2)
        end = time.time()
        print u"222-sleep %fs,第%d次\n,quequ:%s" % (end - begin,count,quequ_.qsize())
        begin = end
        count += 1
import cgi
if __name__=="__main__": 
    
    #testFilter() #测试过滤器与map    
    #testHtmlecscape()#测试html转义字符的处理
    #testReMatch() #测试正则的Match      
    #testJson() #测试json
    #testReSubFindall() #测试正则sub findall
    #testQueue()
    #testDic()
    #b = None
    #a = b.encode('raw_unicode_escape')
    #
    
    #a = u"'"

    #print cgi.escape(a) 



    print 'E:\ZuJuan\WCFUpload\Upload\Program Files\NSE\NSE-SH3\Template\Normal\\temp8.html&lt;u&gt;'.replace("\\","\\\\")
  
    s = u'[{"optionHtml":"&lt;p&gt;&lt;span class=&#39;option&#39;&gt;A、&lt;/span&gt;1、4、7&lt;/p&gt;"},{"optionHtml":"&lt;p&gt;&lt;span class=&#39;option&#39;&gt;B、&lt;/span&gt;2、5、8&lt;/p&gt;"},{"optionHtml":"&lt;p&gt;&lt;span class=&#39;option&#39;&gt;C、&lt;/span&gt;0、3、6、9&lt;/p&gt;"}]'
    arr = json.loads(s)
    arr2=[]
    
    for a in arr:
        ss = re.sub(u'(&lt;p&gt;(.+?)&lt;/span&gt;).+(&lt;/p&gt;)','\g<3>',a['optionHtml'])
        print ss
    arr1 = re.findall(u'{"optionHtml":"&lt;p&gt;.+?&lt;/span&gt;(.+?)&lt;/p&gt;\s*"}[,|\]]',s)
    print json.dumps(arr1,ensure_ascii=False)  
    sssss = u'12（ ））'
    with open('ta.txt','w') as f:
        f.write(sssss)
        f.write(re.sub(u'([^（])（ ））','\g<1>（）',sssss))
    sss = u"&lt;span class&gt;&lt;/span&gt;1.25加0.35得&lt;br/&gt;&lt;div align=right&gt;[ ]&lt;/div&gt;"

    print re.sub(u'&lt;div\s+align=right&gt;(.*?)&lt;/div&gt;','',sss)

    asss = u"宪法具有最高的法律效力  &lt;/td&gt; &lt;/tr&gt;&lt;/table&gt;"
    if asss.find('&lt;table/&gt;') > -1:
        print asss
    else:
        print re.sub(u'&lt;/td&gt;\s*&lt;/tr&gt;\s*&lt;/table&gt;','',asss)
       

    '''
    a = []
    for i in range(20):
        a.append(i if i%4!=0 else None)
    print [ b for b in a if b ]
    #print os.path.join("data/tmp","12/")
    print "data/pic/tiku\source\img\20090807\20090807170321002.jpg-tmp".rstrip('-tmp')
    '''
   