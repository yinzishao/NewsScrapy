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
        item = NewsItem()
        for news in news_list:
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
                    yield item
                else:
                    self.flag= pageindex
            else:
                logger.info("can't find search_result")
        #下一页
        # if int(pageindex)<self.crawl_page:
        if not self.flag:
            next_url = self.page_url % str(articleCursor)
            yield scrapy.Request(next_url,callback=self.parse)
        # soup = BeautifulSoup(response.body,"lxml")
        # page_res = re.search("page=(\d+)",response.url)
        # pageindex = page_res.group(1) if page_res else None #爬取页数
        # search_result = soup.find_all("ul",id="search-result")
        # if search_result:
        #     news_list = search_result[0].find_all("li",class_="news")
        #     print len(news_list)
        #     #新闻列表的新闻，获取图片和摘要
        #     for news in news_list:
        #         news_url = news.a.get("href",None) if news.a else None
        #         abstract =None
        #         if news.find("div",class_="summary hidden-xxs"):
        #             abstract = news.find("div",class_="summary hidden-xxs").string.strip()
        #         pic =news.find("img").get("data-original",None) if news.find("img") else None
        #         item = NewsItem(news_url=news_url,abstract=abstract,pic =pic)
        #         #将item作为元素传递到解析页面中
        #         if news_url:
        #             request = scrapy.Request(news_url,callback=self.parse_news)
        #             request.meta['item'] = item
        #             request.meta['pageindex'] = pageindex
        #             yield request
        #         else:
        #             logger.info("can't find news_url")
        #     #下一页
        #
        #     # if int(pageindex)<self.crawl_page:
        #     if not self.flag:
        #         next_url = self.page_url % str(int(pageindex)+1)
        #         yield scrapy.Request(next_url,callback=self.parse)
        # else:
        #     logger.info("can't find search_result")

    def parse_news(self,response):
        item = response.meta['item']
        pageindex = response.meta['pageindex']
        soup = BeautifulSoup(response.body,"lxml")
        #eg:2016年07月13日 21:50:42
        news_date = soup.find("span",class_="item time").string if soup.find("span",class_="item time") else None
        struct_date = datetime.datetime.strptime(news_date.encode('utf-8'),"%Y年%m月%d日 %H:%M:%S")
        news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")   #规范日期时间
        title = soup.find("h1",class_="article-title").string if soup.find("h1",class_="article-title") else None
        author = soup.find("span",class_="item author").a.string if soup.find("span",class_="item author") else None
        comment_num = soup.find("span",class_="wscn-cm-counter").string if soup.find("span",class_="wscn-cm-counter") else None
        content = soup.find("div",class_="article-content").text if soup.find("div",class_="article-content") else None
        news_no = response.url.rsplit("/",1)[-1]
        item["title"]=title
        item["author"]=author
        item["comment_num"]=comment_num
        item["content"]=content
        item["news_date"]=news_date
        item["crawl_date"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item["news_no"] = news_no
        item["catalogue"] = u"最新文章"
        item = judge_news_crawl(item)   #判断是否符合爬取时间
        if item:
            yield item
        else:
            self.flag= pageindex
