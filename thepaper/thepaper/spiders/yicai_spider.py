#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'
import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("YicaiSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl
from pyvirtualdisplay import Display
from selenium import webdriver
import time
#TODO:


# browser.get('http://www.baidu.com')


class YicaiSpider(scrapy.spiders.Spider):
    name = "yicai"
    allowed_domains = ['yicai.com']
    start_urls = ["http://m.yicai.com/news/business/"]
    flag = 0
    def __init__(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.driver = webdriver.Firefox()

    def parse(self, response):
        self.driver.get('http://m.yicai.com/news/business/')
        index_page_code = self.driver.page_source
        code =index_page_code
        pageindex = 1
        interval =10
        while True:
            soup = BeautifulSoup(code)
            news_list = soup.find_all("dl",class_="f-cb")
            #页数来爬，因为每次都会有之前的新闻.间隔为10
            for news in news_list[interval*(pageindex-1):interval*pageindex]:
                pic = news.find("img").get("src") if news.find("img") else None
                title = news.find("h3").text if news.find("h3") else None
                news_url = news.find("h3").a.get("href") if news.find("h3") else None
                item = NewsItem(pic=pic,title=title,news_url=news_url)
                yield scrapy.Request(news_url,callback=self.parse_news,meta={"item":item,"pageindex":pageindex})
            #触发下一页操作
            if self.flag:
                break
            self.driver.find_element_by_id("clickMore").click()
            time.sleep(1)
            next_page_code =  self.driver.page_source
            code = next_page_code   #更新页面源代码
            pageindex += 1
        self.driver.quit()
        self.display.stop()

    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        pageindex = response.meta.get("pageindex",1)
        origin_url = response.url
        news_no_res = re.search(r"news/(\d+)\.html",origin_url)
        news_no = news_no_res.group(1) if news_no_res else None
        soup = BeautifulSoup(response.body)
        ff3 = soup.find("h2",class_="f-ff3 f-fwn")
        referer_web = soup.find("h2",class_="f-ff3 f-fwn").i.text if ff3 else None
        #日期
        origin_date = soup.find("h2",class_="f-ff3 f-fwn").contents[-1].text if ff3 else None
        struct_date = datetime.datetime.strptime(origin_date,"%Y-%m-%d %H:%M")
        news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
        content = soup.find("div",class_="m-text").text if soup.find("div",class_="m-text") else None
        author = soup.find("h3",class_="f-ff3 f-fwn").span.text if soup.find("h3",class_="f-ff3 f-fwn") else None
        crawl_date = NOW
        item["referer_web"]=referer_web
        item["crawl_date"]=crawl_date
        item["author"]=author
        item["content"]=content
        item["news_no"]=news_no
        item["news_date"]=news_date
        item = judge_news_crawl(item)
        if item:
            yield item
        else:
            self.flag=pageindex




