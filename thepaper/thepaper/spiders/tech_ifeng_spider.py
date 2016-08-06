# -*- coding: utf-8 -*-
__author__ = 'k'

import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("TechIfengSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl
import time

class TechIfeng(scrapy.spiders.Spider):
    domain = 'http://tech.ifeng.com/'
    name = 'tech_ifeng'
    allowed_domains = ['tech.ifeng.com']
    next_url = 'http://tech.ifeng.com/listpage/800/%s/1/rtlist.shtml'
    flag = 0
    start_urls = [
        'http://tech.ifeng.com/listpage/800/%s/1/rtlist.shtml' % (time.strftime("%Y%m%d"))
        #http://tech.ifeng.com/listpage/800/20160805/1/rtlist.shtml
    ]

    def parse(self,response):
        origin_url = response.url
        pageindex = origin_url.rsplit("/",3)[-3]
        soup = BeautifulSoup(response.body,"lxml")
        news_list = soup.find_all("div",class_=re.compile("zheng_list"))
        for news in news_list:
            news_date = news.find("div" ,class_ = "Function").text.strip() if news.find("div" ,class_ = "Function") else None
            if news_date:
                temp = news.find("a" , class_ = "t_css") if news.find("a" , class_ = "t_css") else None
                if not temp:
                    continue
                news_url = temp.get("href")
                title = temp.get("title")
                news_no = news_url.rsplit("/",1)[-1].split(".")[0]
                abstract = news.find("p").text.strip() if news.find("p") else None
                if len(news_date) == 10:
                    news_date = news_date + " 00:00:00"
                else:
                    news_date=news_date + ":00"
                item = NewsItem(news_date=news_date,
                                title=title,
                                abstract=abstract,
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
        nextDate = datetime.datetime(int(pageindex[:4]), int(pageindex[4:6]), int(pageindex[6:8])) - datetime.timedelta(days=1)
        if not self.flag:
            next_url = self.next_url % (nextDate.strftime('%Y%m%d'))
            yield scrapy.Request(next_url)


    def parse_news(self, response):
        item = response.meta.get("item", NewsItem())
        soup = BeautifulSoup(response.body.decode("utf-8").encode("utf-8"),"lxml")
        pic = soup.find("p",class_ = "detailPic").find("img").get("src") if soup.find("p",class_ = "detailPic") else None
        referer_web = soup.find("span",class_ = "ss03").text if soup.find("span",class_ = "ss03") else None
        author = soup.find("span",itemprop="author").find("span").text if soup.find("span",itemprop="author") else None
        temp = soup.find("div" ,id = "main_content")
        if temp:
            ps = temp.find_all("p") if temp.find_all("p") else None
            content = "\n\n".join([ p.text.strip() for p in ps])
        else:
            content = None
        item['pic'] = pic
        item['referer_web'] = referer_web
        item['author'] = author
        item['content'] = content
        item['crawl_date'] = NOW
        yield item