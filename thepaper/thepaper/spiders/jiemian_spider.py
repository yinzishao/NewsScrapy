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

class JiemianSpider(scrapy.spiders.Spider):
    domain = "http://www.jiemian.com"
    name = "jiemian"
    allowed_domains = ["jiemian.com",]
    next_url = "http://a.jiemian.com/index.php?m=index&a=indexAjax&callback=jQuery110206517611923063482_%s&page=%s&_=%s"
    flag = 0
    start_urls = [
        "http://www.jiemian.com/",
    ]

    def parse(self,response):
        origin_url = response.url
        if origin_url == JiemianSpider.start_urls[0]:
            soup = BeautifulSoup(response.body,"lxml")
            pageindex = 1

            catalogue = "左快讯"
            temp = soup.find("ul",class_ = "news-msg-list")
            for news in temp.find_all("div", class_ = "news-msg-item"):
                news_date = "%s %s:00" % (time.strftime("%Y-%m-%d"),news.find("div",class_ = "news-date"))
                title = news.find("a").text.strip()
                news_url = news.find("a").get("href")
                news_no = news_url.rsplit("/",1)[-1].split(".")[0]
                item = NewsItem(news_date=news_date,
                                title=title,
                                news_no = news_no,
                                news_url=news_url,
                                catalogue = catalogue,
                                )
                yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={"item":item})

            catalogue = "左新闻列表"
            temp = soup.find("div",class_ = "news-wrap" )
            for news in temp.find_all("div", class_ = "news-view"):
                pic = news.find("div",class_ = "news-img").find("img").get("src") if news.find("div",class_ = "news-img") else None
                title = news.find("div",class_ = "news-header").find("a").text.strip()
                news_url = news.find("div",class_ = "news-header").find("a").get("href")
                news_no = news_url.rsplit("/",1)[-1].split(".")[0]
                abstract = news.find("div",class_ = "news-main").text.strip()
                author = news.find("span",class_ = "author").text.strip()    if news.find("span",class_ = "author") else None
                read_num = news.find("span",class_ = "collect").text.strip() if news.find("span",class_ = "collect") else None
                comment_num = news.find("span",class_ = "comment").text.strip() if news.find("span",class_ = "comment") else None
                item = NewsItem(
                                title=title,
                                news_no = news_no,
                                news_url=news_url,
                                catalogue = catalogue,
                                pic = pic,
                                abstract = abstract,
                                author = author,
                                read_num = read_num,
                                comment_num = comment_num,
                                )
                yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={"item":item})

            catalogue = "左头条"
            temp = soup.find("div",class_ = "top-slider")
            for news in temp.find_all("div",class_ = "slider-page"):
                news_url = news.find("div",class_ = "slider-header").find("a").get("href")
                if "article" not in news_url:
                    continue
                news_no = news_url.rsplit("/",1)[-1].split(".")[0]
                pic = news.find("div",class_= "slider-img").find("img").get("src") if news.find("div",class_= "slider-img") else None
                topic = news.find("div",class_ = "tags").text.strip()
                title = news.find("div",class_ = "slider-header").text.strip()
                author = news.find("span",class_ = "author").text.strip()
                read_num = news.find("span",class_ = "collect").text.strip()
                comment_num = news.find("span",class_ = "comment").text.strip()
                item = NewsItem(
                                title=title,
                                news_no = news_no,
                                news_url=news_url,
                                catalogue = catalogue,
                                pic = pic,
                                author = author,
                                read_num = read_num,
                                comment_num = comment_num,
                                topic = topic
                                )
                yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={"item":item})
            next_url = self.next_url % (int(time.time()-1),int(pageindex)+1,int(time.time()))
            yield scrapy.Request(next_url)
        else:
            pageindex = origin_url.rsplit("&",1)[0].rsplit("=",1)[-1]
            text =  response.body.split("(",1)[-1][:-1]
            re_json = json.loads(text)
            catalogue = "左新闻列表"
            temp = BeautifulSoup(re_json[0]["rst"],"lxml")
            for news in temp.find_all("div", class_ = "news-view"):
                pic = news.find("div",class_ = "news-img").find("img").get("src") if news.find("div",class_ = "news-img") else None
                title = news.find("div",class_ = "news-header").find("a").text.strip()
                news_url = news.find("div",class_ = "news-header").find("a").get("href")
                news_no = news_url.rsplit("/",1)[-1].split(".")[0]
                abstract = news.find("div",class_ = "news-main").text.strip() if news.find("span",class_ = "news-main") else None
                author = news.find("span",class_ = "author").text.strip() if news.find("span",class_ = "author") else None
                read_num = news.find("span",class_ = "collect").text.strip() if news.find("span",class_ = "collect") else None
                comment_num = news.find("span",class_ = "comment").text.strip() if news.find("span",class_ = "comment") else None
                item = NewsItem(
                                title=title,
                                news_no = news_no,
                                news_url=news_url,
                                catalogue = catalogue,
                                pic = pic,
                                abstract = abstract,
                                author = author,
                                read_num = read_num,
                                comment_num = comment_num,
                                )
                if u"昨天" in news.find("span",class_ = "date").text.strip():
                    self.flag = pageindex
                yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={"item":item})
                if not self.flag:
                    next_url = self.next_url % (int(time.time()-1),int(pageindex)+1,int(time.time()))
                    yield scrapy.Request(next_url)

    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        read_num = soup.find("a",title=u"浏览").text.strip() if soup.find("a",title=u"浏览") else None
        comment_num  = soup.find("span", class_="comment_count").text.strip() if soup.find("span", class_="comment_count") else None
        author = soup.find("span",class_="author").text.strip() if soup.find("span",class_="author") else None
        news_date = soup.find("span", class_="date").text.strip().replace("/","-") + ":00"  if soup.find("span", class_="date") else None
        pic = soup.find("div",class_= "article-img").find("img").get("src").strip() if soup.find("div",class_= "article-img") and soup.find("div",class_= "article-img").find("img") else None
        temp = soup.find("div",class_="article-content")
        content = "\n".join([ t.text.strip() for t in temp.find_all("p")]) if temp.find("p") else None

        item["read_num"] = read_num
        item["author"] = author
        item['comment_num'] = comment_num
        item["news_date"] = news_date
        item['pic'] = pic
        item["content"] = content
        item['crawl_date'] = NOW

        yield item