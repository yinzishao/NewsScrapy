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
logger = logging.getLogger("MeadinSpider")

class MeadinSpider(scrapy.spiders.Spider):
    domain = "http://www.meadin.com/"
    name = "meadin"
    allowed_domains = ["meadin.com",]
    start_urls = [
        "http://info.meadin.com/Index_1.shtml",
    ]

    def parse(self, response):
        html = response.body
        soup = BeautifulSoup(html,"lxml")

        #爬取列表
        viewlist = soup.find_all("div","list list-640")
        if viewlist:
            for news in viewlist:
                title = news.select("h3 a")[0].string if news.select("h3 a") else None
                news_url = news.select("h3 a")[0].get("href",None) if news.select("h3 a") else None
                content = news.select('p[class="info"]')[0].string if news.select('p[class="info"]') else None  #info
                pic = news.find('img').get("src",None) if news.find('img') else None    #图片链接
                #brand
                tags = []                           #标签组
                fl = news.find(class_="clear date")
                if fl and fl.select("a"):
                    topic = fl.select("a")[0].string    #专题
                    for i in fl.select("a")[1:-1]:
                        tags.append(i.string)
                    date = fl.find(class_="fr arial").string
                else:
                    date = None
                    topic=None
                #新闻不是当天的
                if time.strptime(date,"%Y-%m-%d").tm_mday != time.localtime().tm_mday:
                    raise CloseSpider('today scrapy end')

                news_item = NewsItem(title=title,news_url=news_url,content=content,pic=pic,topic=topic,time=date,tags=tags)
                yield news_item

        else:
            logger.info("can't find news list")
        origin_url = response.url
        res = re.search(r'ndex_(.*?)\.shtml',origin_url)
        if res:
            index = res.group(1)
            new_index = int(index)+1
            new_url = re.sub(r'ndex_(.*?)\.shtml','ndex_%s.shtml' % str(new_index),origin_url)
            yield scrapy.Request(new_url)
        else:
            logger.info("can't find index")