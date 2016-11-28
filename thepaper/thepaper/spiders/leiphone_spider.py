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
logger = logging.getLogger("LeiphoneSpider")
from thepaper.settings import *
class LeiphoneSpider(scrapy.spiders.Spider):
    """
    最新文章包括顶部推荐，和精选导读
    """
    domain = "http://www.leiphone.com"
    name = "leiphone"
    allowed_domains = ["leiphone.com",]
    end_day = END_DAY     #终结天数
    end_now = END_NOW
    flag = 0
    next_url = "http://www.leiphone.com/page/%s"
    start_urls = [
        "http://www.leiphone.com/page/1",
    ]
    def parse(self, response):
        url = response.url
        pageindex = url.rsplit("/",1)[-1]
        soup = BeautifulSoup(response.body, "lxml")
        wrap = soup.find("div",class_="lph-pageList index-pageList")
        news_list = wrap.find_all("li")
        for news in news_list:
            topic = news.find("div",class_="img").a.string.strip() if news.find("div",class_="img") else None
            pic = news.find("img").get("data-original",None) if news.find("img") else None
            title = news.find("h3").text.strip() if news.find("h3") else None
            abstract = news.find("div",class_="des").text.strip() if news.find("div",class_="des") else None
            author = news.find("a",class_="aut").text.strip() if news.find("a",class_="aut") else None
            news_url = news.find("h3").a.get("href") if news.find("h3") else None
            tag_list = news.find("div", class_="tags").find_all("a")
            tags = [i.text for i in tag_list] if tag_list else None
            item = NewsItem(topic=topic,
                            news_url=news_url,
                            pic=pic,
                            title=title,
                            abstract=abstract,
                            author=author,
                            tags=tags,
                            )
            request = scrapy.Request(news_url,meta={"item":item,"pageindex":pageindex},callback=self.parse_news)
            yield request
        if not self.flag:
            pageindex = int(pageindex)+1
            next_url = self.next_url % pageindex
            yield scrapy.Request(next_url)
    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        pageindex = response.meta.get("pageindex",1)
        soup = BeautifulSoup(response.body, 'lxml')
        origin_date = soup.find("td", class_="time").text.strip()
        struct_date= datetime.datetime.strptime(origin_date,"%Y-%m-%d %H:%M")
        news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
        content = soup.find("div", class_= "lph-article-comView").text.strip() if soup.find("div", class_= "lph-article-comView").text.strip() else None
        item["news_date"]= news_date
        item["crawl_date"]= NOW
        item["content"] = content
        item["catalogue"] = u"最新资讯"
        item = judge_news_crawl(item)
        if item:
            yield item
        else:
            self.flag = int(pageindex)
