#!/usr/bin/env python
# *-* coding:utf-8 -*-

import os
import re
import urlparse
import requests
import json
import LoggerUtil
from SqlUtil import PostgreSql
from cfg import PATH,SQL
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

logger = LoggerUtil.getLogger(__name__)

def getFilename(url,root_path=PATH.root_path):
    url_path = urlparse.urlsplit(url)      
    return os.path.join(root_path,url_path.path[1:])

def isDownloadFinish(urls):
    urlList = json.loads(urls)
    for url in urlList:
        fileName = getFilename(url)
        if not os.path.exists(fileName): return False
    return True

def main(select_sql=SQL.select_sql_img,update_sql=SQL.update_sql_img):
    postgreSql = PostgreSql()
    count = 0
    total = 0
    try:
        flag = True #代表数据库里面还有需要处理的数据
        id = 0
        while flag:
            try:
                flag = False
                update_params = []
                for rows in postgreSql.getAll(select_sql % id):
                    flag = True
                    total += 1
                    id = rows[0] if rows[0] > id else id
                    qid = rows[1]
                    urls = rows[2]                    
                    try:      
                        if isDownloadFinish(urls):
                            #下载完成就更新t_jyeoo_img_url
                            update_params.append((1,qid))                                           
                    except Exception as ex:
                        logger.exception(u"处理qi=%s，校验题目的所有图片下载是否完成发生异常,异常信息：%s" % (qid,ex.message))                        
                
                if update_params: 
                    postgreSql.batchExecute(update_sql,update_params)
                    postgreSql.commit()                
                count += len(update_params)
                logger.info(u'已成功处理题目数量:%d，校验题目数量总数:%d' % (count,total))
            except Exception as e:
                postgreSql.rollback()
                logger.exception("批量处理-异常信息:%s" %(e.message))
                
    finally:
        postgreSql.close()

if __name__ == '__main__':
    main()