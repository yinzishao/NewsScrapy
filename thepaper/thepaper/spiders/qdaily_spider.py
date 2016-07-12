#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
from scrapy.exceptions import CloseSpider

__author__ = 'yinzishao'

import scrapy
from bs4 import BeautifulSoup
import time
import re
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("QdailySpider")

class QdailySpider(scrapy.spiders.Spider):
    domain = "http://www.qdaily.com/"
    name = "qdaily"
    allowed_domains = ["qdaily.com",]
    end_day = 3     #终结天数
    #爬取新闻的×天前的相对时间，默认当天凌晨。也就是爬取当天凌晨的×天前的新闻
    end_now = datetime.datetime.combine(datetime.date.today(), datetime.time.min) #当天0点
    # end_now = datetime.datetime.now() #当时
    start_urls = [
        "http://www.qdaily.com/tags/29.html"    #top15
    ]

    def parse(self, response):
        soup = BeautifulSoup(response.body,"lxml")
        newslist = soup.find(name="div", attrs={"data-lastkey": True})
        if newslist:

            for i in newslist.children:
                #文章中间有其余无关信息
                if i != u' ':
                    news_url = i.a.get('href',None)
                    pic = i.find("img").get('data-src') if i.find("img") else None
                    title = i.find("h3").string if i.find("h3") else None
                    conment = i.find(class_="iconfont icon-message").string if i.find(class_="iconfont icon-message") else 0
                    heart = i.find(class_="iconfont icon-heart").string if i.find(class_="iconfont icon-heart") else 0
                    topic = i.find(class_="category").span.string if i.find(class_="category") else 0
                    date =None
                    if i.find(name="span", attrs={"data-origindate": True}):
                        date= i.find(name="span", attrs={"data-origindate": True}).get("data-origindate",None)
                        if date:
                            date = date[:-6]
                            struct_date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
                            delta = self.end_now-struct_date
                            if delta.days == self.end_day:
                                raise CloseSpider('today scrapy end')

                    #no content and have heart&conment but not add
                    item = NewsItem(title=title,news_url=news_url,pic=pic,topic=topic,time=date)
                    yield item
            lastkey = newslist.get("data-lastkey",None)
            logger.info(lastkey)
            if lastkey:
                next_url = "http://www.qdaily.com/tags/tagmore/29/%s.json" % lastkey
                yield scrapy.Request(next_url,callback=self.parse_next_page)

        else:
            logger.info("can't find newslit")
    def parse_next_page(self,response):
        data = json.loads(response.body)
        newslist = data['data']["feeds"]
        for news in newslist:
            post = news.get("post",None)
            if post:


                pic = post.get("image",None)
                title = post.get("title",None)
                comment_count = post.get("comment_count",None)
                praise_count = post.get("praise_count",None)    #heart
                topic = post['category']['title']
                id = post.get("id",None)
                datatype = news.get("datatype",None)

                date= post.get("publish_time",None)
                if date:
                    date = date[:-6]

                    #结束条件,对比几天后

                    struct_date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
                    delta = self.end_now-struct_date
                    if delta.days == self.end_day:
                        raise CloseSpider('today scrapy end')
                #文章
                if id and datatype:
                    article_url = self.domain+"%s/%s" % (datatype,id)
                    # yield scrapy.Request(article_url,callback=self.parse_article)
                    news = NewsItem(title=title,news_url=article_url,pic=pic,topic=topic,time=date)
                    yield news
        #下一页
        if data['data']['has_more']:
            last_key = data['data']['last_key']
            next_url = "http://www.qdaily.com/tags/tagmore/29/%s.json" % last_key
            yield scrapy.Request(next_url,callback=self.parse_next_page)



    def parse_article(self,response):
        pass










