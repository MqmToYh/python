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
tmp_suffix = PATH.tmp_suffix

def getJyeooImg(str):
    return re.findall(u'[\"|\'](https?://img.jyeoo.net/.*?)[\\\]?[\"|\']',str)

def getFilename(url,root_path=PATH.root_path):
    url_path = urlparse.urlsplit(url)      
    return os.path.join(root_path,url_path.path[1:])
  
def generateTmpImage(urls):
    '''生成临时的图片文件'''
    for url in urls:
        url_file = getFilename(url)
        tmp_file = url_file+tmp_suffix
        dirname = os.path.dirname(url_file)
        if (not os.path.exists(url_file)) and (not os.path.exists(tmp_file)):
            if not os.path.exists(dirname): os.makedirs(dirname)
            with open(tmp_file,'w+') as f: f.write(url)

def main(select_sql=SQL.select_sql,insert_sql=SQL.insert_sql,update_sql=SQL.update_sql):
    postgreSql = PostgreSql()
    count = 0
    try:
        flag = True #代表数据库里面还有需要处理的数据
        while flag:
            try:
                flag = False
                insert_params = []
                update_params = []
                for rows in postgreSql.getAll(select_sql):
                    flag = True
                    qid = rows[0]
                    try:            
                        urls = []
                        for col in rows[1:]:
                            urls.extend(getJyeooImg(col))
                        #生成临时的图片文件
                        generateTmpImage(urls)
                        #插入数据到img表
                        insert_params.append((qid,json.dumps(urls),0 if urls else 2))                       
                        #更新jyeoo主表的数据状态
                        update_params.append((1 if urls else 2,qid))                       
                    except Exception as ex:
                        logger.exception(u"处理qi=%s，创建题目的图片发生异常,异常信息：%s" % (qid,ex.message))    
                if insert_params: postgreSql.batchExecute(insert_sql,insert_params)
                if update_params: postgreSql.batchExecute(update_sql,update_params)
                postgreSql.commit()
                count += len(update_params)
                logger.info(u'已成功处理题目数量:%d' % count)
            except Exception as e:
                postgreSql.rollback()
                logger.exception("批量处理-异常信息:%s" %(e.message))
                
    finally:
        postgreSql.close()

if __name__ == '__main__':
    main()
