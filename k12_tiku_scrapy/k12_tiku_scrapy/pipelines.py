# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
from k12_tiku_scrapy.items import *

#测试用
class K12TikuScrapyPipeline(object):
    def process_item(self, item, spider):
        print item
        if isinstance(item,KnowledItem) :
            cid_path = 'data/%s-%s/knowled/' % (item['cid'],item['cn'])
            if not os.path.exists(cid_path):
                os.makedirs(cid_path)            
            knowled_file = cid_path+'/%s-download-Knowleds' % item['KnowledId']
            if not os.path.exists(knowled_file):
                with open(knowled_file,'ab') as f:
                    f.write(json.dumps(dict(item),ensure_ascii=False)+'\n')
        return item
