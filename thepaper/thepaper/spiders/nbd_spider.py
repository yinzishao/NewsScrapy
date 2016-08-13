#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'
import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("NbdSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl
class NbdSpider(scrapy.spiders.Spider):
    domain = "http://www.nbd.com.cn"
    name = "nbd"
    allowed_domains = ["nbd.com.cn",]
    next_url = "http://www.nbd.com.cn/columns/3/page/%s"
    flag = 0
    start_urls = [
        "http://www.nbd.com.cn/columns/3/page/1",
    ]
    def parse(self, response):
        origin_url = response.url
        pageindex = origin_url.rsplit("/")[-1]
        soup = BeautifulSoup(response.body,"lxml")
        news_list = soup.find_all("li",class_="mt24 pr")
        for news in news_list:
            news_date = news.find("a",href="javascript:;").text if news.find("a",href="javascript:;") else None
            if news_date:
                news_url = news.find("p",class_="h1").a.get("href",None) if news.find("p",class_="h1") else None
                news_no = news_url.rsplit("/")[-1].split(".")[0]    #http://www.nbd.com.cn/articles/2016-07-25/1025147.html
                title =  news.find("p",class_="h1").text.strip() if news.find("p",class_="h1") else None
                #显示不全，在新闻具体页拿
                # abstract = news.find("p",class_="news-p").text.strip() if news.find("p",class_="news-p") else None
                referer_web =news.find("div",class_="messge").contents[-2].a.text if news.find("div",class_="messge") else None
                referer_web = referer_web if referer_web != '' else None
                comment_num =soup.find("span",class_="fr").a.text if soup.find("span",class_="fr") else None
                item = NewsItem(news_date=news_date,
                                title=title,
                                # abstract=abstract,
                                referer_web=referer_web,
                                comment_num=comment_num,
                                news_no = news_no,
                                news_url=news_url
                                )
                item = judge_news_crawl(item)
                if item:
                    yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={"item":item})
                else:
                    self.flag = pageindex
            else:
                logger.warning("can't find news_date")
        if not self.flag:
            next_url = self.next_url % (int(pageindex)+1)
            yield scrapy.Request(next_url)

    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        #antuhor 两种情况
        if soup.find("div",class_="author"):
            author = soup.find("div",class_="author").find_next("span").text
        else :
            author = soup.find("div",class_="author1").find_next("span").text if soup.find("div",class_="author1") else None
        content = soup.find("div",class_="main-left-article").get_text(strip=True) if soup.find("div",class_="main-left-article") else None
        abstract = soup.find("p",id="prompt").get_text(strip=True) if soup.find("p",id="prompt") else None
        item['author'] = author
        item['content'] =content
        item['abstract'] =abstract
        item['crawl_date']=NOW
        yield item
