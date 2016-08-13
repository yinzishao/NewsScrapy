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

class CntaSpider(scrapy.spiders.Spider):
    domain = "http://www.cnta.gov.cn"
    name = "cnta"
    allowed_domains = ["cnta.gov.cn",]
    flag = {}
    start_urls = [
        "http://www.cnta.gov.cn/xxfb/mrgx/",
        "http://www.cnta.gov.cn/xxfb/jjgat/index.shtml",
        "http://www.cnta.gov.cn/xxfb/xwlb/index.shtml",
        "http://www.cnta.gov.cn/zwgk/tzggnew/gztz/index.shtml",
    ]


    def parse(self,response):
        origin_url = response.url
        if "index" not in origin_url:
            soup = BeautifulSoup(response.body,"lxml")
            catalogue =  soup.find("a",class_ = "blue CurrChnlCls").get("title").strip()
            news_list = soup.find("div", class_ = "lie_main_m").find_all("li")
            for news in news_list:
                title = news.find("a").text.strip()
                news_url = "http://www.cnta.gov.cn/xxfb" + news.find("a").get("href")[2:]
                news_no = news_url.rsplit("/",1)[-1].split(".")[0]
                item = NewsItem(
                        news_url =news_url,
                        title = title,
                        news_no = news_no,
                        catalogue = catalogue,
                    )
                yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={'item':item})
        else:
            topic_url = origin_url.rsplit(".",1)[0]
            self.flag.setdefault(topic_url,0)
            yield scrapy.Request(origin_url,callback=self.parse_topic)

    def parse_topic(self,response):
        origin_url = response.url
        if "_" not in origin_url:
            pageindex = 0
            topic_url = origin_url.rsplit(".",1)[0]
        else:
            temp = origin_url.rsplit("_",1)
            pageindex = temp[-1].split(".",1)[0]
            topic_url = temp[0]
        soup = BeautifulSoup(response.body,"lxml")
        catalogue =  soup.find("a",class_ = "blue CurrChnlCls").get("title").strip()
        news_list = soup.find("div", class_ = "lie_main_m").find_all("li")
        for news in news_list:
            news_date = news.find("span").text.strip() + " 00:00:00"
            title = news.find("a").text.strip()[10:]
            news_url = topic_url.rsplit("/",1)[0] + news.find("a").get("href")[1:]
            news_no = news_url.rsplit("/",1)[-1].split(".")[0]
            item = NewsItem(
                        news_date = news_date,
                        news_url =news_url,
                        title = title,
                        news_no = news_no,
                        catalogue = catalogue,
            )
            item = judge_news_crawl(item)
            if item:
                yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={'item':item})
            else:
                self.flag[topic_url] = pageindex
        if not self.flag[topic_url]:
            next_url = topic_url + "_" + str(int(pageindex) + 1) + ".shtml"
            yield scrapy.Request(next_url,callback=self.parse_topic)


    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body,"lxml")
        temp = soup.find("div",class_ = "main_t").find_all("span")
        news_date = temp[0].text
        referer_web = temp[1].text.split(u"：")[1]
        temp = soup.find("div",class_ = "TRS_Editor")
        content  = "\n\n".join([ t.text.strip() for t in temp.find_all("p")])
        item["news_date"] = news_date
        item["referer_web"] = referer_web
        item["content"] = content
        item['crawl_date'] = NOW
        yield item
