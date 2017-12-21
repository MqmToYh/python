#/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')


from selenium import webdriver

driver = webdriver.Firefox()

driver.get('http://www.zdic.net/')
print driver.title
#print unicode(driver.page_source)
#print driver.dir
driver.close()




def downloadZdic(cn,html_path=PATH.html_zdic_path):
    fileName = os.path.join(html_path,'%s_zdic' % cn)
    if os.path.exists(fileName):return
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.customHeaders.User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36"
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    driver.implicitly_wait(30)
    driver.get('http://www.zdic.net/')
    ele = driver.find_element_by_id('q')
    ele.clear()
    ele.send_keys(cn)
    ele.send_keys(Keys.ENTER)
    driver.implicitly_wait(30)
    assert "No results found." not in driver.page_source   
    assert '%s的解释|%s的意思|汉典“%s”字的基本解释' % (cn,cn,cn) in driver.title
    with open(fileName,'w') as f: f.write(driver.page_source)
    with open(html_path+"cn_url.txt",'a') as f: f.write('%s  %s\n'%(cn,driver.current_url))
    #print driver.current_url
    #print driver.find_element_by_id("daudio").get_attribute('value')
    #print '/p/?mp3='
    driver.close()
def downloadAll(cn_file=PATH.cn_file):
    initdir()
    pool = ThreadPool(10)
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