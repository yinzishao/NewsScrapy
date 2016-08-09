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

class TmtpostSpider(scrapy.spiders.Spider):
    domain = "http://www.tmtpost.com"
    name = "tmtpost"
    allowed_domains = ["tmtpost.com", ]
    next_url = "http://www.tmtpost.com/api/lists/get_index_list?offset=%s&limit=30"
    flag = 0
    start_urls = [
        "http://www.tmtpost.com/api/lists/get_index_list?offset=0&limit=30",
    ]

    def parse(self,response):
        origin_url = response.url
        pageindex = origin_url.rsplit("&",1)[0].split("=",1)[-1]
        dejson = json.loads(response.body)
        news_list = dejson["data"]
        for news in news_list:
            news_date = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(news["time_published"])))
            title = news["title"]
            abstract = news["summary"]
            read_num = news["number_of_reads"]
            comment_num = news["number_of_comments"]
            if len(news["hero_image"]["original"]) > 0:
                pic = news["hero_image"]["original"][0]["url"]
            else:
                pic = None
            news_url = news["short_url"]
            news_no = news_url.rsplit("/",1)[-1].split(".",1)[0]
            author = ",".join([ t["username"] for t in news["authors"]])
            topic = ",".join([ t["tag"] for t in news["tags"]])
            item = NewsItem(news_date=news_date,
                            title=title,
                            abstract=abstract,
                            comment_num=comment_num,
                            news_no=news_no,
                            news_url=news_url,
                            read_num = read_num,
                            pic = pic,
                            author = author,
                            topic = topic
                            )
            item = judge_news_crawl(item)
            if item:
                yield scrapy.Request(item["news_url"], callback=self.parse_news, meta={"item": item})
            else:
                self.flag = pageindex
        if not self.flag:
            next_url = self.next_url % (int(pageindex) + 30)
            yield scrapy.Request(next_url)

    def parse_news(self,response):
        item = response.meta.get("item", NewsItem())
        soup = BeautifulSoup(response.body,"lxml")
        temp = soup.find("div",class_="inner") if soup.find("div",class_="inner") else None
        if temp:
            content = "\n\n".join([ t.text.strip() for t in temp.find_all("p")])
        else:
            content = None
        item["content"] = content
        item['crawl_date']=NOW
        yield item
