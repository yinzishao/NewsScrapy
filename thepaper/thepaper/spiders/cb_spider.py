#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests

__author__ = 'yinzishao'
import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("CbSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl
from pyvirtualdisplay import Display
from selenium import webdriver
import time

class YicaiSpider(scrapy.spiders.Spider):
    name = "cb"
    allowed_domains = ['cb.com.cn']
    domain = "http://www.cb.com.cn"
    next_page_url = "http://www.cb.com.cn/opinion/%s.html"
    start_urls = [
                   next_page_url % 1,
                    # "http://m.yicai.com/news/consumer/"
                  ]
    flag = 0
    def __init__(self):
        self.display = Display(visible=0, size=(800, 600))  #为了隐藏浏览器
        self.display.start()
        # self.chromedriver = "/home/youmi/Downloads/chromedriver"
        # self.driver = webdriver.Chrome(self.chromedriver)              #若无display，会打开浏览器
        chromedriver = "/home/ubuntu/geckodriver"
        self.driver = webdriver.Firefox(executable_path=chromedriver)
    def parse(self, response):
        page = response.meta.get("page",1)
        origin_url = response.url
        self.driver.get(origin_url)
        time.sleep(3)
        code = self.driver.page_source
        soup = BeautifulSoup(code,"lxml")
        news_list = soup.find_all("div",class_="mod-b mod-art ")
        #
        for index,news in enumerate(news_list):

            title = news.find("h3").text if news.find("h3") else None
            news_url =self.domain + news.find("h3").a.get("href",None) if news.find("h3") else None
            pic = news.find("img").get("src",None) if news.find("img") else None
            author = news.find("span",class_="author-name").text if news.find("span",class_="author-name")else None
            comment_num = news.find("span",class_="cy_cmt_count").text if news.find("span",class_="cy_cmt_count") else None
            read_num = news.find_all("em")[1].a.text if news.find_all("em") else None
            abstract = news.find("div",class_="mob-sub").text if news.find("div",class_="mob-sub") else None
            item = NewsItem(
                title=title,
                news_url=news_url,
                pic=pic,
                author=author,
                comment_num=comment_num,
                read_num=read_num,
                abstract=abstract,

            )
            yield scrapy.Request(news_url,callback=self.parse_news,meta={"item":item,"page":page,"index":index})

        #若在这里判断的话，会抛出很多下一页。
        #因为文章的解析很慢，所以首页虽然是结束了，但self.flag因为文章解析慢，一直没有改变，所以一直抛出下一页。
        # if not self.flag:
        #     next_page = page+1
        #     next_page_url = self.next_page_url % next_page
        #     yield scrapy.Request(next_page,meta={"page":next_page})

    def parse_news(self,response):
        # driver = webdriver.Chrome(self.chromedriver)
        driver = webdriver.Firefox(executable_path=self.chromedriver)
        item = response.meta.get("item",NewsItem())
        page = response.meta.get("page",1)
        index = response.meta.get("index",0)
        origin_url = response.url
        no_res = re.search(r"/(\d+)?.html",origin_url)
        news_no = no_res.group(1) if no_res else None
        driver.get(origin_url)
        time.sleep(3)
        code = driver.page_source
        driver.quit()
        soup = BeautifulSoup(code,"lxml")
        # import pdb;pdb.set_trace()
        authors = soup("span",class_="author-name")
        referer_web = None
        for a in authors:
            if "来源".decode("utf-8") in a.text:
                referer_web = a.text[3:]
        news_date = soup.find("span",class_="article-time").text if soup.find("span",class_="article-time") else None
        content = soup.find("div",id="article_content").get_text(strip=True) if soup.find("div",id="article_content") else None
        item["content"]=content
        item["news_date"]=news_date
        item["referer_web"]=referer_web
        item["crawl_date"]=NOW
        item["news_no"]=news_no
        item =judge_news_crawl(item,end_day=2)
        if item:
            yield item
        else:
            self.flag=page

        #把抛出下一页，放到每一页的最后篇文章来判断。
        if index == 19 and not self.flag:
            next_page = page+1
            next_page_url = self.next_page_url % next_page
            yield scrapy.Request(next_page,meta={"page":next_page})
    def closed(self, reason):
        logger.info("Closed:" + reason)
        self.driver.quit()
        self.display.stop()



