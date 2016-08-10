# -*- coding: utf-8 -*-
__author__ = 'k'

import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
import time
logger = logging.getLogger("NbdSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl

class _36krSpider(scrapy.spiders.Spider):
    domain = "http://36kr.com"
    name = "36kr"
    allowed_domains = ["36kr.com", ]
    next_url = "http://36kr.com/api/info-flow/main_site/posts?column_id=&b_id=%s&per_page=20&_=%s000"
    flag = 0
    start_urls = [
        "http://36kr.com/",
    ]

    def parse(self, response):
        origin_url = response.url
        if origin_url == _36krSpider.start_urls[0]:
            temp = re.search('"highProjects\|focus":([\w\W]+?),"editorChoice\|focus"',response.body).group(1)
            news_list = json.loads(temp)
            temp = re.search('"editorChoice\|focus":([\w\W]+?),"feedHeaders\|column"',response.body).group(1)
            news_list.extend(json.loads(temp))
            for news in news_list:
                title = news["title"]
                news_url = news["url"]
                if "36kr.com" not in news_url or ".html" not in news_url:
                    continue
                news_date = news["created_at"]
                pic = news["cover"]
                news_no = news_url.rsplit("/",1)[-1].split(".")[0]
                item = NewsItem(
                        news_date=news_date,
                        title=title,
                        news_no=news_no,
                        news_url=news_url,
                        pic = pic
                        )
                yield scrapy.Request(item["news_url"], callback=self.parse_news, meta={"item": item})
            next_url = _36krSpider.next_url % ("",str(time.time()).split(".")[0])
            yield scrapy.Request(next_url)
        else:
            news_list = json.loads(response.body)["data"]["items"]
            next_id = news_list[-1]["id"]
            for news in news_list:
                title = news["title"]
                news_no = news["id"]
                news_url = "http://36kr.com/p/%s.html" % (news_no)
                if "36kr.com" not in news_url or ".html" not in news_url:
                    continue
                news_date = news["created_at"]
                pic = news["cover"]
                abstract = news["summary"]
                topic = ",".join([ t for t in re.findall('\["([\w\W]+?)",',news["extraction_tags"])])
                catalogue = news["column"]["name"]
                author = news["user"]["name"]
                item = NewsItem(
                    news_date=news_date,
                    title=title,
                    news_no=news_no,
                    news_url=news_url,
                    pic=pic,
                    abstract = abstract,
                    topic = topic,
                    author = author,
                    catalogue = catalogue
                )
                item = judge_news_crawl(item)
                if item:
                    yield scrapy.Request(item["news_url"], callback=self.parse_news, meta={"item": item})
                else:
                    self.flag = 1
            if not self.flag:
                next_url = self.next_url % (next_id,str(time.time()).split(".")[0])
                yield scrapy.Request(next_url)


    def parse_news(self, response):
        item = response.meta.get("item", NewsItem())
        temp = re.search("\"content\":\"([\w\W]+?)\"", response.body).group(1)
        comment_num = re.search('"comment":"([\w\W]+?)"',response.body).group(1)
        print comment_num
        soup = BeautifulSoup(temp)
        content = "\n\n".join([ t.text.strip() for t in soup.find_all("p")])
        item['content'] = content
        item['comment_num'] = comment_num
        item['crawl_date'] = NOW
        yield item
