#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PIL import Image
import Utils
import shutil
import re
import os
import urlparse
import time
import json
from SqlUtil import PostgreSql
from cfg import PATH,SQL,start_time,image_url
import LoggerUtil
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

logger = LoggerUtil.getLogger(__name__)

def getJyeooImg(str):
    return re.findall(u'[\"|\'](https?://img.jyeoo.net/.*?)[\\\]?[\"|\']',str)

def isNotTmpFile(fileName,tmp_suffix=PATH.tmp_suffix):
    return not fileName.endswith(tmp_suffix)

def main(startTime=start_time,select_sql=SQL.select_sql_img,update_sql=SQL.update_sql,
update_sql_img=SQL.update_sql_img,insert_sql=SQL.insert_sql_convert,root_path=PATH.root_path,pic_new_path=PATH.pic_new_path):
    curr_time = time.time()
    curr_time_strft = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(curr_time))
    #记录当前分析时间
    logger.info(u'本次分析时间：%s,秒：%.2f' %(curr_time_strft,curr_time))
    if not os.path.exists(pic_new_path): os.makedirs(pic_new_path)
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
                update_image_params= []
                insert_params = []
                for rows in postgreSql.getAll(select_sql % id):
                    flag = True
                    total += 1
                    id = rows[0] if rows[0] > id else id
                    qid = rows[1]
                    urls = rows[2]                     
                    try:   
                        isDownloadFinish = True 
                        urlMap={}
                        for url in json.loads(urls): 
                            url_path = urlparse.urlsplit(url)                            
                            fileName = os.path.join(root_path,url_path.path[1:])              
                            if os.path.exists(fileName):
                                mtime = os.path.getmtime(fileName)  
                                if mtime >= curr_time:  
                                    isDownloadFinish = False                           
                                elif start_time <= mtime:
                                    (temp,extension) = os.path.splitext(fileName)
                                    #新文件名称
                                    file_new_name= "%s%s" %(Utils.getStrMD5(url+"-mqm"),extension)
                                    #新文件名称 - 全名
                                    file_new_name_all = os.path.join(pic_new_path,file_new_name)
                                    #新的url
                                    url_new = image_url+file_new_name
                                    urlMap[url] = url_new                                    
                                    if not os.path.exists(file_new_name_all):
                                        shutil.copy2(fileName,file_new_name_all)
                                        Utils.modifyMD5(file_new_name_all)                                        
                                        insert_params.append((url,url_new))
                                else:
                                    #表示为之前处理过的图片
                                    sql_url = "select new_jyeoo_url  t_jyeoo_image_convert where old_jyeoo_url = %s"
                                    urlMap[url] = postgreSql.getOne(sql_url,(url))
                                    if urlMap[url]:
                                        logger.error(u'oldurl:%s,数据不存在'% url)
                            else:
                                isDownloadFinish = False

                        #下载完成就更新t_jyeoo_img_url 
                        if isDownloadFinish:
                            update_image_params.append((1,qid))      
                            # 设置替换的图片url、更新原始数据表的状态为3（有图片、图片下载完成）
                            update_params.append((json.dumps(urlMap),3,qid))                       
                                                                      
                    except Exception as ex:
                        logger.exception(u"处理qi=%s，校验题目的所有图片下载是否完成发生异常,异常信息：%s" % (qid,ex.message))                        
                if update_params: postgreSql.batchExecute(update_sql,update_params)
                if update_image_params: postgreSql.batchExecute(update_sql_img,update_image_params)
                if insert_params: postgreSql.batchExecute(insert_sql,insert_params)
                postgreSql.commit()                                
                count += len(update_image_params)
                logger.info(u'已成功处理题目数量:%d，校验题目数量总数:%d' % (count,total))
            except Exception as e:
                postgreSql.rollback()
                logger.exception("批量处理-异常信息:%s" %(e.message))
                
    finally:
        postgreSql.close()

if __name__ == '__main__':
    main()
    