#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'
import re
from scrapy.exceptions import CloseSpider
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("TravelWeeklyChinaSpider")
from thepaper.settings import *

class TravelWeeklyChinaSpider(scrapy.spiders.Spider):
    domain = "http://travelweekly-china.com/"
    name = "twc"
    allowed_domains = ["travelweekly-china.com",]
    end_day = END_DAY     #终结天数
    end_now = END_NOW
    post_next_url = "http://travelweekly-china.com/Dyna.asmx/PageContentList"
    start_urls = [
        "http://travelweekly-china.com/",
        # "http://www.qdaily.com/categories/18.html", #商业
    ]
    #根据首页的新闻类别爬取各个类别的url
    def parse(self, response):
        soup = BeautifulSoup(response.body,"lxml")
        menu = soup.find('div',id="channel---7",class_="channel")
        if menu:
            for topic in menu('ul'):
                topic_name = topic.li.a.string
                url = topic.find("a").get("href",None)
                if url:
                    topic_url = self.domain+url
                    yield scrapy.Request(topic_url,callback=self.parse_topic)
    #根据每个类型的首页得到新闻json的接口与参数
    def parse_topic(self,response):

        """
        爬取下一页的链接
        POST请求
        需要三个参数：
            PageKey
            WidgetId
            PageNumber
        """
        soup = BeautifulSoup(response.body,"lxml")
        next_obj = soup.find("a",class_="insert-more show-more")
        next_pagekey = next_obj.get("_p",None)
        next_wid = next_obj.get("_wid",None)
        # next_num = next_obj.get("_n",None)
        next_num = 1
        post_data = {"req":
                         {
                             "PageKey":next_pagekey,
                             "WidgetId":next_wid,
                             "PageNumber":next_num
                         }
                     }
        yield scrapy.Request(self.post_next_url,
                             callback=self.parse_newslist_json,
                             method="POST",
                             headers={"Content-Type":"application/json"},
                             body=json.dumps(post_data))

    def parse_newslist_json(self,response):
        # if self.post_next_url == response.url:
        res = json.loads(response.body)['d']
        #需要替换<div>因为并没有</div>会影响beautifulsoup的加载！！！
        res = re.sub(re.compile(r'<div.*?>'),"",res)
        news_list = BeautifulSoup(res).find_all("article")
        # else:
        #     soup = BeautifulSoup(response.body,"lxml")
        #     news_list = soup.find('div',class_="start-feed")('article')
        if news_list:
            for news in news_list:
                title = news.span.a.string
                url = news.span.a.get("href",None)
                news.p.a.replace_with("")
                content = unicode(news.p).replace(u'\xa0', u'').replace("<p>","").replace("<\p>","")
                if url:
                    #列表并没有时间，所以不能设定停止条件
                    yield scrapy.Request(self.domain+url,callback=self.parse_news)


        origin_post_data = json.loads(response.request.body)
        post_data = origin_post_data.get("req",None)
        if post_data:
            pagenumber = post_data['PageNumber']
            post_data.update({"PageNumber":str(int(pagenumber)+1)})
        yield scrapy.Request(self.post_next_url,
                             callback=self.parse_newslist_json,
                             method="POST",
                             headers={"Content-Type":"application/json"},
                             body=json.dumps(post_data))


