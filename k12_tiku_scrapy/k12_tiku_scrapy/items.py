# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class K12TikuScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

#测试用
class KnowledItem(scrapy.Item):
    '''知识点条目对象'''
    url = scrapy.Field()
    cid = scrapy.Field()
    cn = scrapy.Field()
    KnowledId = scrapy.Field()
    KnowledName = scrapy.Field()

    
