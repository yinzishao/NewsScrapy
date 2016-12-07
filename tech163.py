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
class Tech163Spider(scrapy.spiders.Spider):
    domain = "http://tech.163.com"
    name = "tech163"
    allowed_domains = ["tech.163.com", ]
    flag = 0
    start_urls = [
        "http://tech.163.com/special/internet_%s/" % (datetime.datetime.today().year),
    ]
    next_url = start_urls[0][0:-1]

    def parse(self,response):
        origin_url = response.url
        if origin_url == Tech163Spider.start_urls[0]:
            pageindex = 1
        else:
            pageindex = int(origin_url.split("_")[2][0:-1])
        soup = BeautifulSoup(response.body, "lxml")
        news_list = soup.find("ul",class_ = "newsList").find_all("li")
        for news in news_list:
            temp = news.find("p",class_ = "sourceDate").text.strip()
            news_date = temp[-19:]
            if news_date:
                referer_web = temp[:-19]
                comment_num = 0     #news.find("a", class_ = "commentCount  ").text.strip()   #评论条数需要用模拟器获取
                temp = news.find("div",class_="titleBar clearfix").find("a")
                news_url = temp.get("href")
                title = temp.text.strip()
                news_no = news_url.rsplit("/",1)[-1][:-5]
                item = NewsItem(
                                news_date=news_date,
                                title=title,
                                referer_web=referer_web,
                                comment_num=comment_num,
                                news_no=news_no,
                                news_url=news_url
                                )
                item = judge_news_crawl(item)
                if item:
                    yield scrapy.Request(item["news_url"], callback=self.parse_news, meta={"item": item})
                else:
                    self.flag = pageindex
            else:
                logger.warning("can't find news_date")
        if not self.flag:
            pageindex = pageindex + 1
            if pageindex < 10:
                pageindex = '0' + str(pageindex)
            else:
                pageindex = str(pageindex)

            next_url = self.next_url + "_%s/" % (pageindex)
            yield scrapy.Request(next_url)

    def parse_news(self, response):
        item = response.meta.get("item", NewsItem())
        soup = BeautifulSoup(response.body)
        temp = soup.find("div",class_="post_text") if soup.find("div",class_="post_text") else None
        if temp:
            pic = temp.find("img").get("src") if temp.find("img") else None
            content = "\n\n".join([t.text.strip() for t in temp.find_all("p")])
        else:
            pic = None
            content = None
        item["pic"] = pic
        item["content"] = content
        item['crawl_date'] = NOW
        yield item
