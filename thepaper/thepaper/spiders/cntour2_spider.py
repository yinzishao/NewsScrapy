#-*- coding: utf-8 -*-
# @Time    : 16-12-7 下午3:57
# @File    : cntour2_spider.py
# @Software: PyCharm

__author__ = "K"

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


class Cntour2Spider(scrapy.spiders.Spider):
    domain = "http://www.cntour2.com"
    name = "cntour2"
    allowed_domains = ["cntour2.com", ]

    start_urls = [
        "http://www.cntour2.com/",
    ]

    def parse(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        news_list = soup.find("div",class_="main_l").find_all("li")
        for news in news_list:
            catalogue = "新闻热点"
            news_url = Cntour2Spider.start_urls[0][:-1] + news.find("a").get("href")
            title = news.find("a").text.strip()
            news_no = news_url.rsplit("/",1)[-1].split(".")[1]
            item = NewsItem(
                title=title,
                news_no=news_no,
                news_url=news_url,
                catalogue = catalogue
            )
            yield scrapy.Request(item["news_url"], callback=self.parse_news, meta={"item": item})

    def parse_news(self, response):
        item = response.meta.get("item", NewsItem())
        soup = BeautifulSoup(response.body)
        # topic = soup.find("div","navItem").find_all("a")[2].text if len(soup.find("div","navItem").find_all("a")) >= 3 else None

        temp = soup.find("div",class_= "actTitle")
        news_date = re.search('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',temp.text)
        referer_web = temp.find("a").text if temp.find("a") else None
        referer_url = temp.find("a").get("href") if temp.find("a") else None

        temp =  soup.find("div",class_="content")
        content = "\n".join([ t.text.strip() for t in  temp.find_all("p")])
        pic = Cntour2Spider.start_urls[0][:-1] + temp.find("img").get("src") if temp.find("img") else None

        # item["topic"] = topic
        item["news_date"] = news_date
        item["referer_web"] = referer_web
        item["referer_url"] = referer_url
        item["pic"] = pic
        item["content"] = content
        item['crawl_date'] = NOW

        yield item