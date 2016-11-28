#!/usr/bin/env python
# -*- coding:utf-8 -*-
from thepaper.util import judge_news_crawl

__author__ = 'yinzishao'

import re
from scrapy.exceptions import CloseSpider
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("WallstreetcnSpider")
from thepaper.settings import *

class Wallstreetcn(scrapy.spiders.Spider):
    domain = "http://wallstreetcn.com/"
    name = "wallstreetcn"
    allowed_domains = ["wallstreetcn.com"]
    end_day = END_DAY
    end_now = END_NOW
    crawl_page = 5  #爬取的页面限制
    index_page = 1  #开始页面数
    flag = 0        #是否爬取下一页，当结束时flag为停止页面数
    page_url = "https://api.wallstreetcn.com/v2/pcarticles?limit=20&category=most-recent&articleCursor=%s"
    start_urls = [
        page_url % 0
    ]
    def parse(self,response):
        pageindex = response.meta.get('pageindex', 1)
        data = json.loads(response.body)
        news_list = data['posts']
        articleCursor = data['articleCursor']
        for news in news_list:
            item = NewsItem()
            news_data = news.get("resource",None)
            if news_data:
                createdAt = news_data.get("createdAt", None)
                struct_date = datetime.datetime.utcfromtimestamp(int(createdAt))+ datetime.timedelta(hours=8)
                news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")   #规范日期时间
                item["news_date"]=news_date
                item["title"]=news_data.get("title", None)
                item["comment_num"]=news_data.get("commentCount", None)
                item["pic"]=news_data.get("imageUrl", None)
                item["news_no"]=news_data.get("id", None)
                item["title"]=news_data.get("title", None)
                news_url = news_data.get("url", None)
                item["news_url"] = news_url
                item["abstract"] = news_data.get("summary", None)
                item["author"] = news_data.get("user", None).get("screenName", None) if news_data.get("user", None) else None
                item = judge_news_crawl(item)   #判断是否符合爬取时间
                if item:
                    request = scrapy.Request(news_url,callback=self.parse_news)
                    request.meta['item'] = item
                    yield request
                else:
                    self.flag= pageindex
            else:
                logger.info("can't find search_result")
        #下一页
        # if int(pageindex)<self.crawl_page:
        if not self.flag:
            next_url = self.page_url % str(articleCursor)
            yield scrapy.Request(next_url,callback=self.parse)

    def parse_news(self,response):
        item = response.meta['item']
        soup = BeautifulSoup(response.body,"lxml")
        content = soup.find("div",class_="page-article-content").text.strip() if soup.find("div",class_="page-article-content") else None
        item["content"]=content
        item["catalogue"] = u"最新文章"
        yield item
