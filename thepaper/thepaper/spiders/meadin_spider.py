#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'

import scrapy
from bs4 import BeautifulSoup
import re
from thepaper.items import NewsItem

class MeadinSpider(scrapy.spiders.Spider):
    domain = "http://www.meadin.com/"
    name = "meadin"
    allowed_domains = ["meadin.com",]
    start_urls = [
        "http://info.meadin.com/Index.shtml",
    ]

    def parse(self, response):
        html = response.body
        soup = BeautifulSoup(html,"lxml")

        #爬取列表
        viewlist = soup.find_all("div","list list-640")
        if viewlist:
            for news in viewlist:
                title = news.select("h3 a")[0].string if news.select("h3 a") else None
                news_item = NewsItem()


        else:
            pass