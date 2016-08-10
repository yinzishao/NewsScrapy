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

class IheimaSpider(scrapy.spiders.Spider):
    domain = "http://www.iheima.com"
    name = "iheima"
    allowed_domains = ["iheima.com", ]
    next_url = "http://www.iheima.com"
    flag = 0
    start_urls = [
        "http://www.iheima.com/",
    ]
    def parse(self,response):
        origin_url = response.url
        if "page" not in origin_url:
            pageindex = 1
        else:
            pageindex = origin_url.split("&",1)[0].rsplit("=",1)[-1]
        soup = BeautifulSoup(response.body,"lxml")
        news_list = soup.find_all("article", class_="item-wrap cf")
        for news in news_list:
            news_date = news.find("span" , class_ = "timeago").text.strip() if news.find("span" , class_ = "timeago") else None
            if news_date:
                title = news.find("a" ,class_ = "title").text.strip()
                news_url = news.find("a" ,class_ = "title").get("href")
                abstract = news.find("div",class_ = "brief").text.strip()
                author = news.find("span" , class_ = "name").text.strip()
                news_no = news_url.rsplit("/",1)[-1].split(".")[0]
                item = NewsItem(news_date=news_date + ":00",
                            title=title,
                            abstract=abstract,
                            news_no=news_no,
                            news_url=news_url,
                            author = author
                            )
                item = judge_news_crawl(item)
                if item:
                    yield scrapy.Request(item["news_url"], callback=self.parse_news, meta={"item": item})
                else:
                    self.flag = pageindex
            else:
                logger.warning("can't find news_date")
        if not self.flag:
            if pageindex == 1:
                next_url = self.next_url + soup.find("a" , class_ = "more").get("href")
            else:
                next_url = self.next_url + "/?page=" + str(int(pageindex) + 1) + "&" + origin_url.split("&",1)[-1]
            headers = {
                "X-Requested-With":"XMLHttpRequest"
                }
            yield scrapy.Request(next_url,headers=headers,)

    def parse_news(self, response):
        item = response.meta.get("item", NewsItem())
        soup = BeautifulSoup(response.body,"lxml")
        temp = soup.find("div",class_ = "main-content") if soup.find("div",class_ = "main-content") else None
        if temp :
            content = "\n\n".join([ t.text.strip() for t in temp.find_all("p")])
        else:
            content = None
        item["content"] = content
        item['crawl_date'] = NOW
        yield item
