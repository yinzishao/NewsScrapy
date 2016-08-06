# -*- coding: utf-8 -*-
__author__ = 'k'

import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("ToptourSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl

class ToptourSpider(scrapy.spiders.Spider):
    domain = 'http://www.toptour.cn/'
    name = 'toptour'
    #allowed_domains = ['toptour.cn']
    start_urls = [
        'http://www.toptour.cn/home/'
    ]

    def parse(self , response):
        origin_url = response.url
        soup = BeautifulSoup(response.body,"lxml")
        temp_soup = soup.find('div',id = "ess_ctr10789_ModuleContent") if soup.find('div',id = "ess_ctr10789_ModuleContent") else None
        if temp_soup:
            news_list = temp_soup.find_all("a" , href = re.compile("http://www.toptour.cn/tab"))
            for news in news_list:
                news_url = news.get("href")
                title = news.text.strip()
                item = NewsItem(
                    news_url = news_url,
                    title = title,
                    catalogue = u"右推荐"
                )
                yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={'item':item})
        else:
            logger.warning("%s can't find news_list " % origin_url)


    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        content = soup.find("td",id = "zoom").find_all("p") if soup.find("td",id = "zoom") else None
        content = "\n".join([ c.text.strip() for c in content])
        pattern = "发布时间：([\w\W]+?)&"
        try:
            news_date = re.search(pattern,response.body).group(1)
        except:
            news_date = None
        item["content"] = content
        item["news_date"] = news_date
        yield item