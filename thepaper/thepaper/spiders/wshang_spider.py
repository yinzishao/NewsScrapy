#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'
"""
手机版没有cookie，更方便
但是pc版的首页是所有分类混在一起的
手机版则是新闻在各个分类，所以爬取的时候需要爬各个分类。
"""

import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("WshangSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl
#TODO:
class NbdSpider(scrapy.spiders.Spider):
    """
    最新文章包括顶部推荐
    """
    domain = "http://m.iwshang.com/"
    name = "wshang"
    # allowed_domains = ["i.wshang.com",]
    flag = {}
    start_urls = [
        "http://m.iwshang.com/",
    ]
    #pc端新闻页面url
    pc_news_url = "http://i.wshang.com/Post/Default/Index/pid/%s.html"
    def parse(self, response):
        """

        :param response:
        :return:抛出每个类别的post请求

                post参数：
                    inslider
                    page
                    pagesize
                Content-Type:application/x-www-form-urlencoded
        """
        soup = BeautifulSoup(response.body)
        menu = soup.find_all("a",class_="ui-more")  #所有的类别的链接
        if menu:
            for topic in menu:
                topic_name = topic.text.replace(u"查看","")
                topic_url = topic.get("href")
                self.flag.setdefault(topic_url,0)
                page="1"
                #post_data需要字符串
                post_data = {
                    "inslider":"0",
                    "page":page,
                    "pagesize":"10"
                }
                # yield scrapy.Request(topic_url,
                #                      callback=self.parse_topic,
                #                      method="POST",
                #                      headers={"Content-Type":"application/x-www-form-urlencoded"},
                #                      body=json.dumps(post_data)
                #                      )
                yield scrapy.FormRequest(
                    url=topic_url,
                    formdata=post_data,
                    callback=self.parse_topic,
                    meta={"page":page,"topic_name":topic_name}
                )
    def parse_topic(self,response):
        topic_url = response.url
        # print topic_url
        body = json.loads(response.body)
        news_list = body["data"]
        page = response.meta.get("page","1")
        topic_name = response.meta.get("topic_name",None)
        #http://m.iwshang.com/category/20 没有新闻
        if not news_list:
            self.flag[topic_url]=page
        for news in news_list:
            news_date_timestamp = news.get("published",None)
            struct_date = datetime.datetime.fromtimestamp(int(news_date_timestamp))
            news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
            title = news.get("title",None)
            news_no = news.get("contentid",None)
            abstract = news.get("description",None)
            pic = news.get("thumb",None)
            news_url = news.get("url",None)                 #手机端新闻页面链接
            referenceid = news.get("referenceid",None)      #pc端的id，手机端的id跟pc端的id不一样
            pc_news_url = self.pc_news_url % referenceid    #pc端新闻页面链接
            item = NewsItem(
                news_date=news_date,
                title=title,
                news_no=news_no,
                abstract=abstract,
                pic=pic,
                news_url=pc_news_url,
                topic=topic_name
            )
            item = judge_news_crawl(item)
            if item:
                # yield item
                yield scrapy.Request(pc_news_url,callback=self.parse_news,meta={"item":item})
            else:

                self.flag[topic_url]=page
        if not self.flag[topic_url]:
            page = str(int(page)+1)
            post_data = {
                    "inslider":"0",
                    "page":page,
                    "pagesize":"10"
                }
            yield scrapy.FormRequest(
                    url=topic_url,
                    formdata=post_data,
                    callback=self.parse_topic,
                    meta={"page":page}
                )
    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        #手机
        # content = soup.find("div",id="content-show").get_text(strip=True) if soup.find("div",id="content-show") else None
        #pc
        content = soup.find("div",class_="article-cont").get_text(strip=True) if soup.find("div",class_="article-cont") else None
        article_head = soup.find("div",class_="article-head")
        author=None
        if article_head:
            author = article_head.p.text.split(u"／")[1]

        article_tag_list = soup.find("div",class_="article-tag")("a") if soup.find("div",class_="article-tag") else []
        tags = [tag.text for tag in article_tag_list]
        item["tags"] = tags
        item["author"] = author
        item["content"] = content
        item["crawl_date"] = NOW
        item["catalogue"] = u"最新内容"
        yield item
