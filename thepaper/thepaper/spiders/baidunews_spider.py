#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'youmi'

import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("WshangSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl
import datetime
class BaiduNewsSpider(scrapy.spiders.Spider):
    domain = "http://news.baidu.com/"
    name = "baidunews"
    url_demo = "http://news.baidu.com/ns?ct=0&pn=%s&rn=50&ie=utf-8&tn=newstitle&word=%s" # 参数pn表示跳过前面多少条新闻   word表示关键词

    def start_requests(self):
        url = self.url_demo % (0,"在线旅游")
        print url
        yield scrapy.Request(url, callback=self.parse, meta= {'keyword': '在线旅游'})

    def parse(self, response):
        keyword = response.meta.get("keyword", None)
        soup = BeautifulSoup(response.body,"lxml")
        for t in soup.find_all("div", attrs={"class":"result title"}):
            item = NewsItem()
            url = t.find("a").get("href")       #新闻url
            title = t.find("a").text            #新闻标题
            temp_list = t.find("div",attrs={"class":"c-title-author"}).text.split(u"\xa0\xa0")
            website_name = temp_list[0]         #新闻网站名称、
            news_time = temp_list[1]
            #TODO: Some error
            now = datetime.datetime.now()
            if u"分钟前" in news_time:
                print news_time[:-3]
                struct_date = now - datetime.timedelta(minutes=int(news_time[:-3]))
                news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
            elif u"小时前" in news_time:
                print news_time[:-3]
                struct_date = now - datetime.timedelta(hours=int(news_time[:-3]))
                news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                news_date = "%s-%s-%s %s:00" % (news_time[:4],news_time[5:7],news_time[8:10],news_time[12:])

            item['news_url'] = url
            item['title'] = title
            item['news_date'] = news_date
            item['referer_web'] = website_name
            item["crawl_date"] = NOW
            item["keywords"] = [keyword]
            item = judge_news_crawl(item)
            if item:
                yield item
