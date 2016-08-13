# -*- coding: utf-8 -*-
__author__ = 'k'

import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("NbdSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl
import time

class DonewsSpider(scrapy.spiders.Spider):
    domain = "http://www.donews.com/net/"
    name = "donews"
    allowed_domains = ["donews.com",]
    flag = {}
    start_urls = [
        "http://www.donews.com/net/",
        "http://www.donews.com/original/",
    ]
    def parse(self,response):
        origin_url = response.url
        topic_url = origin_url[:-1]
        self.flag.setdefault(topic_url,0)
        yield scrapy.Request(origin_url,callback=self.parse_topic)

    def parse_topic(self,response):
        origin_url = response.url
        temp = origin_url.rsplit("/",1)
        topic_url = temp[0]
        if temp[1] == "":
            pageindex = 1
        else:
            pageindex = temp[1].split("_",1)[-1].split(".",1)[0]
        soup = BeautifulSoup(response.body,"lxml")
        catalogue = soup.find("div",class_ ="arttitle").text.strip()
        news_list = soup.find("ul",class_ = "art_list mt11").find_all("li")
        for news in news_list:
            title_info = news.find("h5",class_= "title")
            text_info = news.find("div",class_ = "text")
            news_date = text_info.find("span",class_ = "time").text
            news_date = "%s-%s-%s %s:00" % (time.strftime("%Y"),int(news_date[0:2]),int(news_date[3:5]),news_date[7:])
            author = text_info.find("span",class_ = "place").text.strip()
            if author == "":
                author = None
            abstract = text_info.find("p",class_ = "info").text.strip()
            pic = text_info.find("img").get("src") if text_info.find("img") else None
            title = title_info.find("a").text.strip()
            news_url = title_info.find("a").get("href")
            temp = news_url.split("/")
            news_no = temp[-2] + "_" + temp[-1].split(".")[0]
            item = NewsItem(
                    news_url =news_url,
                    news_date = news_date,
                    title = title,
                    abstract = abstract,
                    author = author,
                    news_no = news_no,
                    catalogue = catalogue,
                    pic = pic,
            )
            item = judge_news_crawl(item)
            if item:
                yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={'item':item})
            else:
                self.flag[topic_url] = pageindex
        if not self.flag[topic_url]:
            next_url = "%s/index_%s.html" % (topic_url,int(pageindex) + 1)
            yield scrapy.Request(next_url,callback=self.parse_topic)


    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body,"lxml")
        referer_web = soup.find("span", id= "source_baidu").text if soup.find("span", id= "source_baidu") else None
        temp = soup.find("div",id = "arttext")
        if item["pic"] == None:
            item["pic"] = temp.find("img").get("src") if temp.find("img")  else None
        content = "\n\n".join([ t.text.strip() for t in temp.find_all("p")])
        item['referer_web'] = referer_web
        item['content'] = content
        item['crawl_date'] = NOW
        yield item