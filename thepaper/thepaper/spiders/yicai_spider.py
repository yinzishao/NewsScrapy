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

class YicaiSpider(scrapy.spiders.Spider):
    name = "yicai"
    allowed_domains = ['yicai.com']
    start_urls = [
                    "http://m.yicai.com/news/business/",
                    # "http://m.yicai.com/news/consumer/"
                  ]
    flag = {"http://m.yicai.com/news/business/":0,"http://m.yicai.com/news/consumer/":0}
    def __init__(self):
        self.display = Display(visible=0, size=(800, 600))  #为了隐藏浏览器
        self.display.start()
        # chromedriver = "/home/youmi/Downloads/chromedriver"
        # self.driver = webdriver.Chrome(chromedriver)                   #若无display，会打开浏览器
        chromedriver = "/home/ubuntu/geckodriver"
        self.driver = webdriver.Firefox(executable_path=chromedriver)
    def parse(self, response):
        topic_url = response.url
        catalogue = u"商业" if "business" in topic_url else u"消费"
        self.driver.get(topic_url)                      #打开页面
        index_page_code = self.driver.page_source       #页面源代码
        code =index_page_code
        pageindex = 1
        interval =10
        while True:
            soup = BeautifulSoup(code,"lxml")
            news_list = soup.find_all("dl",class_="f-cb")
            #页数来爬，因为每次都会有之前的新闻.间隔为10
            for news in news_list[interval*(pageindex-1):interval*pageindex]:
                pic = news.find("img").get("src") if news.find("img") else None
                title = news.find("h3").text if news.find("h3") else None
                news_url = news.find("h3").a.get("href") if news.find("h3") else None
                item = NewsItem(pic=pic,title=title,news_url=news_url,catalogue=catalogue)
                yield scrapy.Request(news_url,callback=self.parse_news,meta={"item":item,
                                                                             "pageindex":pageindex,
                                                                            "topic_url":topic_url})
            #结束
            if self.flag[topic_url]:
                break
            #触发下一页操作，追加在页面，而不是打开一个新的页面
            self.driver.find_element_by_id("clickMore").click()    #找到“更多”按钮，触发点击操作
            time.sleep(1)           #等浏览器渲染
            next_page_code =  self.driver.page_source
            code = next_page_code   #更新页面源代码
            pageindex += 1

        #如果放在start_urls一起爬取的话，会报错。原因应该是display不支持并行。
        #现在只能是把每个页面分开
        yield scrapy.Request("http://m.yicai.com/news/consumer/",callback=self.parse)
        # values = self.flag.values()
        # end_conditon = [ v for v in values if not v]    #所有的values都不是0时为[]
        # if not end_conditon:
        #     self.driver.quit()
        #     self.display.stop()

    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        pageindex = response.meta.get("pageindex",1)
        topic_url = response.meta.get("topic_url",None)
        origin_url = response.url
        news_no_res = re.search(r"news/(\d+)\.html",origin_url)
        news_no = news_no_res.group(1) if news_no_res else None
        soup = BeautifulSoup(response.body,"lxml")
        ff3 = soup.find("h2",class_="f-ff3 f-fwn")
        referer_web = soup.find("h2",class_="f-ff3 f-fwn").i.text if ff3 else None
        #日期
        origin_date = soup.find("h2",class_="f-ff3 f-fwn").contents[-1].text if ff3 else None
        struct_date = datetime.datetime.strptime(origin_date,"%Y-%m-%d %H:%M")
        news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
        content = soup.find("div",class_="m-text").text.strip() if soup.find("div",class_="m-text") else None
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
            self.flag[topic_url]=pageindex

    def close(self, reason):
        self.driver.quit()
        self.display.stop()



