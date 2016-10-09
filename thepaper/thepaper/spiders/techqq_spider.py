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
from thepaper.util import judge_news_crawl,judge_key_words
import time

class TechQQSpider(scrapy.spiders.Spider):
    domain = "http://tech.qq.com"
    name = "techqq"
    allowed_domains = ["tech.qq.com"]
    next_date_url = "http://tech.qq.com/l/%s/scroll_%s.htm"
    flag = 0
    start_urls = [
        "http://tech.qq.com/l/%s/scroll_%s.htm" % (time.strftime("%Y%m"),time.strftime("%d"))
    ]

    def parse(self,response):
        origin_url = response.url

        temp = origin_url.rsplit("/",2)
        year_month = temp[-2]
        day = temp[-1][7:9]
        pageindex = datetime.datetime(int(year_month[:4]), int(year_month[4:]), int(day)) - datetime.timedelta(days=1)
        pageindex = pageindex.strftime('%Y%m%d')

        soup = BeautifulSoup(response.body,"lxml")
        temp = soup.find("div",class_="mod newslist") if soup.find("div",class_="mod newslist") else None
        if temp:
            news_list = temp.find_all("li")
            for news in news_list:
                news_url = news.find("a").get("href")
                title = news.find("a").text.strip()
                news_no = news_url.rsplit("/",1)[-1].replace(".htm","")
                temp = news.find("span").text
                news_date = "%s-%s-%s %s:%s" % (time.strftime("%Y"),temp[0:2],temp[3:5],temp[7:],"00")
                item = NewsItem(news_date=news_date,
                                title=title,
                                news_no = news_no,
                                news_url=news_url
                                )
                item = judge_news_crawl(item)
                if item:
                    yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={"item":item})
                else:
                    self.flag = pageindex
        else:
            logger.warning("can't find news_list")
        temp = soup.find_all("a",class_ = "f12") if soup.find("a",class_ = "f12") else None
        today_text_url = None
        if temp:
            for t in temp:
                if u"下一页" in t:
                    today_text_url = t.get("href")
        if today_text_url:
            yield scrapy.Request(today_text_url)
        else:
            if not self.flag:
                next_url = self.next_date_url % (pageindex[0:6],pageindex[6:])
                yield scrapy.Request(next_url)

    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body.decode("gbk"),"lxml")
        referer_web = soup.find("span",bosszone="jgname").text if soup.find("span",bosszone="jgname") else None
        referer_url = soup.find("span",bosszone="jgname").get("href")  if soup.find("span",bosszone="jgname") else None
        abstract = soup.find("p",class_="Introduction").text.strip() if soup.find("p",class_="Introduction") else None
        temp = soup.find("p",align="center") if soup.find("p",align="center") else None
        if temp:
            pic = temp.find("img").get("src") if temp.find("img") else None
        else:
            pic = None
        author = soup.find("span",class_="auth").text if soup.find("span",class_="auth") else None
        crawl_date = NOW
        catalogue = "热点推荐"
        comment_num = soup.find("em",id="top_count").text.strip() if soup.find("em",id="top_count") else None
        temp = soup.find_all("p",style="TEXT-INDENT: 2em") if soup.find("p",style="TEXT-INDENT: 2em") else None
        if temp:
            content = "\n\n".join([ t.text.strip() for t in temp])
        else:
            content = None

        item["referer_web"] = referer_web
        item["referer_url"] = referer_url
        item["abstract"] = abstract
        item["pic"] = pic
        item["author"] = author
        item["crawl_date"] = crawl_date
        item["catalogue"] = catalogue
        item["comment_num"] = comment_num
        item["content"] = content
        item['crawl_date'] = NOW
        item_keywords = judge_key_words(item)  #获得item和关键词匹配的词
        if item_keywords:   #筛选出有关键词的item
            item["keywords"] = item_keywords
            yield item
