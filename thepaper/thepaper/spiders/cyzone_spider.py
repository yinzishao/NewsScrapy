#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'
import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("CyzoneSpider")
from thepaper.settings import *
class CyzoneSpider(scrapy.spiders.Spider):
    domain = "http://www.cyzone.cn/"
    name = "cyzone"
    allowed_domains = ["cyzone.cn",]
    end_day = END_DAY     #终结天数
    end_now = END_NOW
    flag = 0
    #中间推荐板块
    middle_next_url = "http://api.cyzone.cn/index.php?m=content&c=index&a=init&tpl=index_page&page=%s"
    strat_middle_next_url =middle_next_url % 1
    start_urls = [
        strat_middle_next_url,
    ]
    #TODO
    def parse(self, response):
        soup = BeautifulSoup(response.body)
        news_list = soup.find_all("div",class_="article-item clearfix")
        for news in news_list:
            title =news.find("a",class_="item-title").text if news.find("a",class_="item-title") else None
            pic = news.find("img").get("src",None) if news.find("img") else None

