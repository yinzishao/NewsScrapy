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
    page_url = "http://wallstreetcn.com/news?status=published&type=news&order=-created_at&limit=30&page=%s"
    start_urls = [
        page_url % index_page
    ]
    def parse(self,response):
        soup = BeautifulSoup(response.body,"lxml")
        search_result = soup.find_all("ul",id="search-result")
        if search_result:
            news_list = search_result[0].find_all("li",class_="news")
            print len(news_list)
            #新闻列表的新闻，获取图片和摘要
            for news in news_list:
                news_url = news.a.get("href",None) if news.a else None
                abstract =None
                if news.find("div",class_="summary hidden-xxs"):
                    abstract = news.find("div",class_="summary hidden-xxs").string.strip()
                else:None

                pic =news.find("img").get("data-original",None) if news.find("img") else None
                item = NewsItem(news_url=news_url,abstract=abstract,pic =pic)
                #将item作为元素传递到解析页面中
                request = scrapy.Request(news_url,callback=self.parse_news)
                request.meta['item'] = item
                if news_url:
                    yield request
                else:
                    logger.info("can't find news_url")
            #下一页
            page_res = re.search("page=(\d+)",response.url)
            page = page_res.group(1) if page_res else None
            if int(page)<self.crawl_page:
                next_url = self.page_url % str(int(page)+1)
                yield scrapy.Request(next_url,callback=self.parse)
        else:
            logger.info("can't find search_result")

    def parse_news(self,response):
        item = response.meta['item']
        soup = BeautifulSoup(response.body,"lxml")
        #eg:2016年07月13日 21:50:42
        news_date = soup.find("span",class_="item time").string if soup.find("span",class_="item time") else None
        struct_date = datetime.datetime.strptime(news_date.encode('utf-8'),"%Y年%m月%d日 %H:%M:%S")
        #超过结束限期，结束
        delta = self.end_now-struct_date
        if delta.days == self.end_day:
            raise CloseSpider('today scrapy end')
        title = soup.find("h1",class_="article-title").string if soup.find("h1",class_="article-title") else None
        author = soup.find("span",class_="item author").a.string if soup.find("span",class_="item author") else None
        conment_num = soup.find("span",class_="wscn-cm-counter").string if soup.find("span",class_="wscn-cm-counter") else None
        content = soup.find("div",class_="article-content").text if soup.find("div",class_="article-content") else None
        news_no = response.url.rsplit("/",1)[-1]
        item["title"]=title
        item["author"]=author
        item["conment_num"]=conment_num
        item["content"]=content
        item["news_date"]=news_date
        item["crawl_date"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item["news_no"] = news_no
        yield item


