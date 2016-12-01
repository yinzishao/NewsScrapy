# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import json
import pymongo
import logging
from settings import SPIDER_NAME
from util import judge_key_words
from scrapy.exceptions import DropItem
from bson.objectid import ObjectId

class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open('items.txt', 'wb')

    def process_item(self, item, spider):
        item_keywords = judge_key_words(item)#获得item和关键词匹配的词
        if item_keywords:   #筛选出有关键词的item
            item["keywords"] = item_keywords
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

'''
确定关键词
'''
class selectKeywordPipeline(object):

    def process_item(self, item, spider):
        item_keywords = judge_key_words(item)#获得item和关键词匹配的词
        if item_keywords:   #筛选出有关键词的item
            item["keywords"] = item_keywords
            return item
        else:
            logger = logging.getLogger(spider.name)
            logger.info("No keyword in %s" % item["news_url"])
            raise DropItem("No keyword in %s" % item["news_url"])

'''
存放数据库
'''
class MongoPipeline(object):

    collection_name = 'news'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item['source'] = SPIDER_NAME[spider.name]
        item['_id'] = str(ObjectId())
        collection_name = "wechat" if spider.name == "wechat" else self.collection_name
        self.db[collection_name].insert(dict(item))
        return item
