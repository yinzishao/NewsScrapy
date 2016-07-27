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
logger = logging.getLogger("CyzoneSpider")
from thepaper.settings import *
class CyzoneSpider(scrapy.spiders.Spider):
    domain = "http://www.cyzone.cn/"
    name = "cyzone"
    allowed_domains = ["cyzone.cn",]
    end_day = END_DAY     #终结天数
    end_now = END_NOW
    mid_flag = 0    #中间推荐停止标志
    quick_flag = 0  #快报停止标志
    quick_page = 1  #快报开始爬取页面，首页
    #中间推荐板块
    # TODO:首页有推荐的文章并不出现在api中
    middle_next_url = "http://api.cyzone.cn/index.php?m=content&c=index&a=init&tpl=index_page&page=%s"
    quick_url = "http://www.cyzone.cn/category/8/"
    #根据快报首页获取最后一篇快报的时间戳
    quick_json_url = "http://www.cyzone.cn/index.php?m=content&c=index&a=init&tpl=page_kuaixun&inputtime=%s"
    strat_middle_next_url =middle_next_url % 1
    # start_urls = [
    #     strat_middle_next_url,
    # ]
    #开始爬取页面
    def start_requests(self):
        #中间推荐模板
        mid_request = scrapy.Request(self.strat_middle_next_url,callback=self.parse)
        #快报
        qic_request = scrapy.Request(self.quick_url,callback=self.parse_quick)
        return [mid_request,qic_request]

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
                            news_date=news_date,
                            catalogue=u"中间推荐模板")
            item = judge_news_crawl(item)
            if item:
                request = scrapy.Request(news_url,meta={"item":item},callback=self.parse_news)
                yield request
            else:
                self.mid_flag =int(pageindex)
        if not self.mid_flag:
            pageindex = int(pageindex)+1
            next_url = self.middle_next_url % pageindex
            yield scrapy.Request(next_url)
    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        content = soup.find("div",class_="article-content").text
        tag_list = soup.find_all("a","tag-link")
        tags = [i.text for i in tag_list] if tag_list else None
        item["content"] = content
        item["tags"] = tags
        item["crawl_date"]=NOW
        yield item

    def parse_quick(self,response):
        soup = BeautifulSoup(response.body)
        news_list_inner = soup.find("div",class_="list-inner")
        next_timestamp=None

        news_list = news_list_inner.find_all("div",class_=re.compile(r"bulletin-item.*")) if news_list_inner else None
        #json 页面
        if not news_list:
            news_list = soup.find_all("div",class_=re.compile(r"bulletin-item.*"))
        for index,news in enumerate(news_list):
            origin_date = news.find("div",class_="news-time").get("data-time",None) if news.find("div",class_="news-time") else None
            next_timestamp = origin_date if index == len(news_list)-1 else None #取最后一篇文章的时间戳作下一页的时间戳
            struct_date = datetime.datetime.fromtimestamp(int(origin_date))
            news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
            title =news.find("a",class_="item-title").text if news.find("a",class_="item-title") else None
            news_url =news.find("a",class_="item-title").get("href",None) if news.find("a",class_="item-title") else None
            pic = news.find("img").get("src",None) if news.find("img") else None
            content =news.find("div",class_="item-desc").text if news.find("div",class_="item-desc") else None
            id_result = re.search(r"/(\d+)\.html",news_url)
            news_no = id_result.group(1) if id_result else None
            item = NewsItem(content=content,
                            news_url=news_url,
                            pic=pic,
                            title=title,
                            news_no=news_no,
                            news_date=news_date,
                            catalogue=u"快报")
            item = judge_news_crawl(item)
            if item:
                request = scrapy.Request(news_url,meta={"item":item},callback=self.parse_quick_news)
                yield request
            else:
                self.quick_flag =int(self.quick_page)

        if not self.quick_flag:
            if next_timestamp:
                next_quick_url = self.quick_json_url % next_timestamp
                yield scrapy.Request(next_quick_url,callback=self.parse_quick)
            else:
                logger.warning("can't find next_timestamp,url is %s " % response)

    def parse_quick_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        referer_web = soup.find("span",class_="name").text if soup.find("span",class_="name") else None
        tag_list = soup.find_all("a","tag-link")
        tags = [i.text for i in tag_list] if tag_list else None
        item["tags"] = tags
        item['referer_web'] = referer_web
        item['crawl_date'] = NOW
        yield item




