#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'

import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("WshangSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl
"""
网站过时，最新6/15
"""
class NbdSpider(scrapy.spiders.Spider):
    domain = "http://i.wshang.com/"
    name = "wshang"
    allowed_domains = ["i.wshang.com",]
    # next_url = "http://www.nbd.com.cn/columns/3/page/%s"
    flag = 0
    start_urls = [
        "http://i.wshang.com/",
    ]

    def parse(self, response):
        token = re.search(r'YII_CSRF_TOKEN":"(.*?)"',response.body).group(1)
        soup = BeautifulSoup(response.body)
        index_news_list=soup.find_all("div",class_="fcon")
        for index_news in index_news_list:
            index_news_url = index_news.find("span",class_="shadow").a.get("href") if index_news.find("span",class_="shadow") else None
            index_news_title = index_news.find("span",class_="shadow").a.text if index_news.find("span",class_="shadow") else None


