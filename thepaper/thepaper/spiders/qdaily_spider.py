#!/usr/bin/env python
# -*- coding:utf-8 -*-
from thepaper.util import judge_news_crawl

__author__ = 'yinzishao'

from scrapy.exceptions import CloseSpider
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("QdailySpider")
from thepaper.settings import *

class QdailySpider(scrapy.spiders.Spider):
    domain = "http://www.qdaily.com/"
    name = "qdaily"
    allowed_domains = ["qdaily.com",]
    end_day = END_DAY     #终结天数
    end_now = END_NOW
    top_flag = 0
    com_flag = 0
    start_urls = [
        "http://www.qdaily.com/tags/29.html",    #top15
        "http://www.qdaily.com/categories/18.html", #商业
    ]

    def parse(self, response):
        soup = BeautifulSoup(response.body,"lxml")
        newslist = soup.find(name="div", attrs={"data-lastkey": True})
        lastkey = newslist.get("data-lastkey",None)
        logger.info(lastkey)
        if not lastkey:
            logger.warning("can't find next page")
        else:
            if newslist:
                for i in newslist.children:
                    #文章中间有其余无关信息
                    if i != u' ':
                        news_url = self.domain+i.a.get('href',None)
                        pic = i.find("img").get('data-src') if i.find("img") else None
                        title = i.find("h3").string if i.find("h3") else None
                        comment_num = i.find(class_="iconfont icon-message").string if i.find(class_="iconfont icon-message") else 0
                        heart = i.find(class_="iconfont icon-heart").string if i.find(class_="iconfont icon-heart") else 0
                        topic = i.find(class_="category").span.string if i.find(class_="category") else 0
                        news_date =None
                        if i.find(name="span", attrs={"data-origindate": True}):
                            news_date= i.find(name="span", attrs={"data-origindate": True}).get("data-origindate",None)
                            if news_date:
                                news_date = news_date[:-6]

                        #no content and have heart&conment but not add
                        item = NewsItem(title=title,news_url=news_url,pic=pic,topic=topic,news_date=news_date,comment_num=comment_num)
                        # 所属目录
                        item['catalogue'] = "Top 15" if "tags" in response.url else u"商业"
                        #判断是否结束
                        item = judge_news_crawl(item)
                        if item :
                            request = scrapy.Request(news_url,callback=self.parse_article)
                            request.meta["item"] = item
                            yield request
                        else:
                            if "tags" in response.url:
                                self.top_flag = lastkey
                            else:
                                self.com_flag = lastkey
                next_url = None
                #判断各个类别是否需要爬取下一页
                if "tags" in response.url:
                    if not self.top_flag:
                        next_url = "http://www.qdaily.com/tags/tagmore/29/%s.json" % lastkey
                else:
                    if not self.com_flag:
                        next_url = "http://www.qdaily.com/categories/categorymore/18/%s.json" % lastkey
                # logger.info(next_url)
                if next_url:
                    yield scrapy.Request(next_url,callback=self.parse_next_page)
            else:
                logger.warning("can't find newslit")
    def parse_next_page(self,response):
        data = json.loads(response.body)
        newslist = data['data']["feeds"]
        last_key = data['data']['last_key'] if data['data']['has_more'] else None
        for news in newslist:
            post = news.get("post",None)
            if post:


                pic = post.get("image",None)
                title = post.get("title",None)
                comment_num = post.get("comment_count",None)
                praise_count = post.get("praise_count",None)    #heart
                topic = post['category']['title']
                id = post.get("id",None)
                datatype = news.get("datatype",None)

                news_date= post.get("publish_time",None)
                if news_date:
                    news_date = news_date[:-6]
                #文章
                if id and datatype:
                    news_url = self.domain+"%s/%s" % (datatype+"s",id)
                    item = NewsItem(title=title,news_url=news_url,pic=pic,topic=topic,news_date=news_date,comment_num=comment_num)
                    item['catalogue'] = "Top 15" if "tags" in response.url else u"商业"
                    item = judge_news_crawl(item)
                    if item :
                        request = scrapy.Request(news_url,callback=self.parse_article)
                        request.meta["item"] = item
                        yield request
                    else:
                        if "tags" in response.url:
                            self.top_flag = last_key
                        else:
                            self.com_flag = last_key
        #下一页
        next_url = None
        if "tags" in response.url:
            if not self.top_flag:
                next_url = "http://www.qdaily.com/tags/tagmore/29/%s.json" % last_key
        else:
            if not self.com_flag:
                next_url = "http://www.qdaily.com/categories/categorymore/18/%s.json" % last_key
        if next_url:
            yield scrapy.Request(next_url,callback=self.parse_next_page)



    def parse_article(self,response):
        #content,news_no,crawl_date
        item = response.meta.get("item",NewsItem())
        # news_date = item.get("news_date",None)
        # if news_date:
        #     struct_date = datetime.datetime.strptime(news_date,"%Y-%m-%d %H:%M:%S")
        #     delta = self.end_now-struct_date
        #     print delta.days
        #     if delta.days == self.end_day:
        #         raise CloseSpider('today scrapy end')
        soup =BeautifulSoup(response.body)
        author = soup.find("span",class_="name").text if soup.find("span",class_="name") else None
        abstract =  soup.find("p",class_="excerpt").text if soup.find("p",class_="excerpt") else None
        content = soup.find("div",class_="detail").text if soup.find("div",class_="detail") else None
        news_no = response.url.split("/")[-1][:-5]
        item["author"] = author
        item["abstract"] = abstract
        item["content"] = content
        item["crawl_date"] = NOW
        item["news_no"] = news_no
        yield item






