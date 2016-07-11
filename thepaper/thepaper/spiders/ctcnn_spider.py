#!/usr/bin/env python
# -*- coding:utf-8 -*-
from scrapy.exceptions import CloseSpider

__author__ = 'yinzishao'

import scrapy
from bs4 import BeautifulSoup
import time
import re
import logging
from thepaper.items import NewsItem
logger = logging.getLogger("CtcnnSpider")

class CtcnnSpider(scrapy.spiders.Spider):
    domain =  "http://www.ctcnn.com/"
    name = "ctcnn"
    allowed_domains = ["ctcnn.com",]
    # start_urls = [
    #     "http://www.ctcnn.com/json/index_article.jsp?t=1468244608275"
    # ]
    start_url =  "%sjson/index_article.jsp?t=%s" % (domain,int(time.time()))
    def start_requests(self):
        return [
            scrapy.FormRequest(self.start_url,formdata={'page':'1'}),
            scrapy.Request("http://www.ctcnn.com/",callback=self.parse_index)
        ]
    def parse_index(self,response):
        soup = BeautifulSoup(response.body,"lxml")
        index_list = soup.find(class_="index-first-list")("li") if soup.find(class_="index-first-list") else None
        for news in index_list:
            title = news.h2.a.string if news.h2.a else None
            content = news.p.string if news.p else None
            news_url = self.domain+news.a.get("href",None) if news.a else None
            item = NewsItem(title=title,content=content,news_url=news_url)
            yield item

    def parse(self, response):
        soup = BeautifulSoup(response.body,"lxml")
        li = soup.find_all('li')
        if li:
            for news in li :
                title = news.find(class_="title").string if news.find(class_="title") else None
                news_url = self.domain+news.find(class_="title").a.get("href",None) if news.find(class_="title") else None
                content = news.find(class_="info").string if news.find(class_="info") else None
                pic = self.domain+news.find('img').get('src',None) if news.find('img') else None
                topic = news.find(class_="type").string if news.find(class_="type") else None
                date = news.find(class_="time").string[2:] if news.find(class_="time") else None
                struct_date = time.strptime(date,"%Y-%m-%d %H:%M")
                if struct_date.tm_mday != time.localtime().tm_mday:
                    raise CloseSpider('today scrapy end')
                item = NewsItem(title=title,news_url=news_url,content=content,pic=pic,topic=topic,time=date)
                yield item
        else:
            logger.info("can't find news list")

        page =response.request.body.split('=')[-1]
        #下一页
        new_request = scrapy.FormRequest(self.start_url,formdata={'page':str(int(page)+1)})
        yield new_request