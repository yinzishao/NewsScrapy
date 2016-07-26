#!/usr/bin/env python
# -*- coding:utf-8 -*-
from thepaper.util import judge_news_crawl

__author__ = 'yinzishao'
import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("Transport163")
from thepaper.settings import *
class Transport163Spider(scrapy.spiders.Spider):
    domain = "http://money.163.com/"
    name = "163"
    allowed_domains = ["money.163.com",]
    end_day = END_DAY     #终结天数
    end_now = END_NOW
    flag = 0
    start_urls = ["http://money.163.com/special/002526O5/transport.html"]
    next_url = "http://money.163.com/special/002526O5/transport_%s.html"
    def parse(self, response):
        origin_url = response.url
        #http://money.163.com/special/002526O5/transport_02.html
        search_result = re.search(r"_(\d)*?\.",origin_url)
        #获取页数
        pageindex = search_result.group(1) if search_result else 1
        soup = BeautifulSoup(response.body,"lxml")
        news_list = soup("div",class_="list_item clearfix")
        for news in news_list:
            news_date = news.find("span",class_="time").text if news.find("span",class_="time")else None
            title = news.find("h2").text if news.find("h2") else None
            news_url = news.find("h2").a.get("href",None) if news.find("h2") else None
            abstract = news.find("p").contents[0] if news.find("p") else None
            item = NewsItem(title=title,news_url=news_url,abstract=abstract,news_date=news_date)
            item = judge_news_crawl(item)   #判断是否符合爬取时间
            if item:
                request = scrapy.Request(news_url,callback=self.parse_news,meta={"item":item})
                yield request
            else:
                self.flag = int(pageindex)
        if not self.flag:
            next_url = self.next_url % int(pageindex)+1
            yield scrapy.Request(next_url)
    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        referer_web = soup.find("a",id="ne_article_source").text if soup.find("a",id="ne_article_source") else None
        referer_url = soup.find("a",id="ne_article_source").get("href",None) if soup.find("a",id="ne_article_source") else None
        comment_num = soup.find("a",class_="post_cnum_tie").text if soup.find("a",id="ne_article_source") else None
        content = soup.find("div",class_="post_text").text.strip() if soup.find("div",class_="post_text") else None
        #格式: 本文来源：证券日报-资本证券网  作者：矫　月
        author_source = soup.find("span",class_="left").text if soup.find("span",class_="left") else None
        #TODO 作者编码出错
        # import pdb;pdb.set_trace()
        # author = re.search(u"作者(.*)",author_source).group(1)[1:] if author_source else None
        # item["author"]=author
        item["referer_web"]=referer_web
        item["referer_url"]=referer_url
        item["comment_num"]=comment_num
        item["content"]=content
        item["crawl_date"]=NOW
        yield item
