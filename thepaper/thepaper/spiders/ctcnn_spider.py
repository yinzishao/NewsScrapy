#!/usr/bin/env python
# -*- coding:utf-8 -*-
from scrapy.exceptions import CloseSpider
from thepaper.util import judge_news_crawl

__author__ = 'yinzishao'

import scrapy
from bs4 import BeautifulSoup
import time
import re
import logging
from thepaper.items import NewsItem
import datetime
logger = logging.getLogger("CtcnnSpider")
from thepaper.settings import *
class CtcnnSpider(scrapy.spiders.Spider):
    end_day = END_DAY
    end_now = END_NOW
    domain =  "http://www.ctcnn.com/"
    name = "ctcnn"
    # allowed_domains = ["ctcnn.com",]
    # start_urls = [
    #     "http://www.ctcnn.com/json/index_article.jsp?t=1468244608275"
    # ]
    flag=0
    start_url =  "%sjson/index_article.jsp?t=%s" % (domain,int(time.time()))
    def start_requests(self):
        return [
            scrapy.Request("http://www.ctcnn.com/",callback=self.parse),
            # scrapy.FormRequest(self.start_url,formdata={'page':'1'},callback=self.parse_newest),  #TODO something wrong

        ]
    #首页的原创内容
    def parse(self,response):
        yield scrapy.FormRequest(self.start_url,formdata={'page':'1'},callback=self.parse_newest)
        soup = BeautifulSoup(response.body,"lxml")

        index_list = soup.find(class_="index-first-list")("li") if soup.find(class_="index-first-list") else None
        for news in index_list:
            title = news.h2.a.string if news.h2.a else None
            abstract = news.p.string if news.p else None
            news_url = self.domain+news.a.get("href",None) if news.a else None
            item = NewsItem(title=title,abstract=abstract,news_url=news_url,catalogue=u"原创内容")
            request = scrapy.Request(news_url,self.parse_news,dont_filter=True)
            request.meta["item"] = item
            yield request

    #最新内容的列表
    def parse_newest(self, response):
        soup = BeautifulSoup(response.body,"lxml")
        page =response.request.body.split('=')[-1]
        li = soup.find_all('li')
        if li:
            for news in li :
                news_date = news.find(class_="time").string[2:] if news.find(class_="time") else None
                struct_date = datetime.datetime.strptime(news_date,"%Y-%m-%d %H:%M")
                news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
                title = news.find(class_="title").string if news.find(class_="title") else None
                news_url = self.domain+news.find(class_="title").a.get("href",None) if news.find(class_="title") else None
                abstract = news.find(class_="info").string if news.find(class_="info") else None
                pic = self.domain+news.find('img').get('src',None) if news.find('img') else None
                topic = news.find(class_="type").string if news.find(class_="type") else None
                item = NewsItem(catalogue=u"最新内容",
                                title=title,
                                news_url=news_url,
                                abstract=abstract,
                                pic=pic,
                                topic=topic,
                                news_date=news_date)
                item = judge_news_crawl(item)
                if item:
                    request = scrapy.Request(news_url,callback=self.parse_news,dont_filter=True)
                    request.meta["item"] = item
                    yield request
                else:
                    self.flag=page
        else:
            logger.info("can't find news list")


        #下一页
        if not self.flag:
            new_request = scrapy.FormRequest(self.start_url,formdata={'page':str(int(page)+1)},callback=self.parse_newest)
            yield new_request
    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body,"lxml")
        topic,referer_web,author,news_date=None,None,None,None
        #article_type:topic,出处，作者，发布时间
        article_type = soup.find("div",class_="article-type")
        if article_type:
            topic = article_type.a.string   #专题
            span_list = article_type("span")
            if span_list:
                referer_web = span_list[0].text #出处
                author = span_list[1].text  #作者
                news_date = span_list[2].text   #发布时间
        #内容
        content = soup.find("div",class_="article-content").text if soup.find("div",class_="article-content") else None
        #评论次数
        comment_num = soup.find("div",class_="jl-comment-title").span.string if soup.find("div",class_="jl-comment-title") else None
        #新闻编号
        news_no = response.url.split("/")[-1][:-5]

        item['content']=content
        item['referer_web']=referer_web
        item['author']=author
        item['news_date']=news_date
        item['comment_num']=comment_num
        item['crawl_date'] =NOW
        item['topic']=topic
        item['news_no']=news_no

        yield item
        #
        #
        #
        #



