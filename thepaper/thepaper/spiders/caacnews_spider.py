# -*- coding: utf-8 -*-
__author__ = 'k'
import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("CaacnewsSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl

class CaacnewsSpider(scrapy.spiders.Spider):
    domain = "http://www.caacnews.com.cn"
    name = "caacnews"
    allowed_domains = ["caacnews.com.cn", ]
    next_url = "http://www.caacnews.com.cn/n/n13.aspx?pageid=%s"
    flag = 0
    start_urls = [
        "http://www.caacnews.com.cn/n/n13.aspx?pageid=1",
    ]

    def parse(self,response):
        origin_url = response.url
        pageindex = origin_url.rsplit("=",1)[-1]
        soup = BeautifulSoup(response.body,"lxml")
        news_temp = soup.find("table" ,class_ = "list").find("table" , border="0").find("tbody")
        if not news_temp:
            return
        news_list = news_temp.find_all("tr")[1:]
        for news in news_list:
            temp = news.find("a")
            news_url = temp.get("href")
            title = temp.text.strip()
            temp = news.find_all("span")
            referer_web = temp[0].text.strip()
            news_date = temp[1].text.strip()
            news_no = news_url.rsplit("=",1)[-1]
            item = NewsItem(news_date=news_date,
                            title=title,
                            referer_web=referer_web,
                            news_url=news_url,
                            news_no = news_no
                            )
            item = judge_news_crawl(item)
            if item:
                yield scrapy.Request(item["news_url"], callback=self.parse_news, meta={"item": item})
            else:
                self.flag = pageindex
        if not self.flag:
            next_url = self.next_url % (int(pageindex) + 1)
            yield scrapy.Request(next_url)

    def parse_news(self, response):
        item = response.meta.get("item", NewsItem())
        soup = BeautifulSoup(response.body)
        author = soup.find("td",class_ = "t1_td2_02").find_all("span")[1].text if soup.find("td",class_ = "t1_td2_02") else None
        pic = soup.find("p",align="center").find("img").get("src") if soup.find("td",align="center") else None
        temp = soup.find("td",class_="t1_td1")
        content = "\n\n".join([ p.text.strip() for p in temp.find_all("p")])
        item['author'] = author
        item['pic'] = pic
        item['content'] = content
        yield item