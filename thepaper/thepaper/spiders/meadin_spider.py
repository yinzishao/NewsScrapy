#!/usr/bin/env python
# -*- coding:utf-8 -*-
from scrapy.exceptions import CloseSpider
from thepaper.util import judge_news_crawl

__author__ = 'yinzishao'

import scrapy
from bs4 import BeautifulSoup
import time
import re
import logging
from thepaper.items import NewsItem
from thepaper.settings import *
logger = logging.getLogger("MeadinSpider")
import pdb
class MeadinSpider(scrapy.spiders.Spider):
    domain = "http://www.meadin.com/"
    name = "meadin"
    allowed_domains = ["meadin.com",]
    start_urls = [
        "http://info.meadin.com/Index_1.shtml",
    ]
    end_day = END_DAY
    end_now = END_NOW
    flag = 0

    def parse(self, response):
        soup = BeautifulSoup(response.body,"lxml")
        origin_url = response.url
        res = re.search(r'ndex_(.*?)\.shtml',origin_url)
        new_index=1
        if res:
            index = res.group(1)
            new_index = int(index)+1
        #爬取列表
        viewlist = soup.find_all("div","list list-640")
        if viewlist:
            for news in viewlist:
                title = news.select("h3 a")[0].string if news.select("h3 a") else None
                news_url = news.select("h3 a")[0].get("href",None) if news.select("h3 a") else None
                abstract = news.select('p[class="info"]')[0].string if news.select('p[class="info"]') else None  #info
                pic = news.find('img').get("src",None) if news.find('img') else None    #图片链接
                #brand
                tags = []                           #标签组
                fl = news.find(class_="clear date")
                if fl and fl.select("a"):
                    topic = fl.select("a")[0].string    #专题
                    for i in fl.select("a")[1:-1]:
                        tags.append(i.string)
                    news_date = fl.find(class_="fr arial").string   #%Y-%m-%d
                else:
                    news_date = None
                    topic=None


                item = NewsItem(title=title,news_url=news_url,abstract=abstract,pic=pic,topic=topic,news_date=news_date,catalogue=u"咨询")
                request = scrapy.Request(news_url,callback=self.parse_news)
                request.meta['item']=item
                request.meta['pageindex']=index
                yield request

        else:
            logger.info("can't find news list")
        if not self.flag and new_index:
            new_url = re.sub(r'ndex_(.*?)\.shtml','ndex_%s.shtml' % str(new_index),origin_url)
            yield scrapy.Request(new_url)
        else:
            logger.info("can't find index")

    def parse_news(self,response):
        #content,news_date,news_no,crawl_date,referer_web
        item = response.meta.get("item",NewsItem())
        pageindex = response.meta.get("pageindex",1)
        soup = BeautifulSoup(response.body)
        # news_date = item.get("news_date",None)
        #需要爬取具体的时间
        news_date = soup.find("span",class_="arial").text if soup.find("span",class_="arial") else None
        #http://info.meadin.com/PictureNews/2938_1.shtml Exception
        if news_date:

            # struct_date = datetime.datetime.strptime(news_date,"%Y-%m-%d %H:%M:%S")
            # delta = self.end_now-struct_date
            # if delta.days == self.end_day:
            #     raise CloseSpider('today scrapy end')
            referer_web = list(soup.find("p",class_="source").strings)[-1] if soup.find("p",class_="source") else None
            #爬取正文
            art,content = None,None
            art = soup.find("div",class_="article js-article")
            if art:
                #剔除摘要！
                art.find("div",class_="intro").replace_with("")
                content =art.text.strip()
            news_no =response.url.split("/")[-1].split("_")[0]
            item["news_date"]=news_date
            item["content"]=content
            item["referer_web"]=referer_web
            item["crawl_date"]=NOW
            item["news_no"]=news_no
            item = judge_news_crawl(item)
            if item:
                yield item
            else:
                self.flag = pageindex
        else:
            logger.warning("can't find news_date.the url is %s" % response.url)
