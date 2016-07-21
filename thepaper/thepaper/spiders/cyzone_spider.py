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
    # TODO:首页有推荐的文章并不出现在api中
    middle_next_url = "http://api.cyzone.cn/index.php?m=content&c=index&a=init&tpl=index_page&page=%s"
    quick_url = "http://www.cyzone.cn/category/8/"
    strat_middle_next_url =middle_next_url % 1
    start_urls = [
        strat_middle_next_url,
    ]
    def start_requests(self):
        pass

    def parse(self, response):
        origin_url = response.url
        result = re.search(r"page=(\d+)",origin_url)
        # import pdb;pdb.set_trace()
        pageindex = result.group(1) if result else None

        soup = BeautifulSoup(response.body)
        news_list = soup.find_all("div",class_="article-item clearfix")
        for news in news_list:

            info = news.find("div",class_="item-push-info")
            author = info.text[:-3] if info else None
            news_date = info.span.get("data-time") if info.span else None   #时间戳
            struct_date = datetime.datetime.fromtimestamp(int(news_date))
            news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
            delta = self.end_now-struct_date
            print delta.days,"delta day ~~~~~~~~~~~~~~~~"
            if delta.days > self.end_day-1:
                self.flag =int(pageindex)
            else:
                title =news.find("a",class_="item-title").text if news.find("a",class_="item-title") else None
                news_url =news.find("a",class_="item-title").get("href",None) if news.find("a",class_="item-title") else None
                abstract =news.find("p",class_="item-desc").text if news.find("p",class_="item-desc") else None
                pic = news.find("img").get("src",None) if news.find("img") else None
                id_result = re.search(r"/(\d+)\.html",news_url)
                news_no = id_result.group(1) if id_result else None
                item = NewsItem(abstract=abstract,
                                news_url=news_url,
                                pic=pic,
                                title=title,
                                author=author,
                                news_no=news_no,
                                news_date=news_date)
                request = scrapy.Request(news_url,meta={"item":item},callback=self.parse_news)
                yield request
        if not self.flag:
            pageindex = int(pageindex)+1
            next_url = self.middle_next_url % pageindex
            yield scrapy.Request(next_url)
    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        content = soup.find("div",class_="article-content").text
        item["content"] = content
        item["crawl_date"]=NOW
        yield item





