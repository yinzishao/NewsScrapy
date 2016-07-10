#!/usr/bin/env python
# -*- coding:utf-8 -*-
from scrapy.exceptions import CloseSpider

__author__ = 'yinzishao'

import scrapy
from bs4 import BeautifulSoup
import re
from thepaper.items import NewsItem


class ThepaperSpider(scrapy.spiders.Spider):
    domain = "http://www.thepaper.cn/"
    name = "thepaper"
    allowed_domains = ["thepaper.cn"]
    start_urls = [
        # "http://www.thepaper.cn",
        "http://www.thepaper.cn/index_masonry.jsp",
    ]

    def parse(self, response):
        #首页内容
        html = response.body
        soup = BeautifulSoup(html,"lxml")
        #爬取首页新闻列表
        for i in self.fetch_newslist(soup):
            # raise CloseSpider(str(i['time'] == u"一天前"))
            if i['time'] == "一天前": raise CloseSpider("today news end")
            yield i

        #爬取下一页的链接
        lasttime = "nothing"
        for i in  soup.select('div[class="news_li"]'):
            if i.attrs.has_key("lasttime"):
                lasttime =  i["lasttime"]
                break
        #得到下一个url的连接。
        # 格式：load_chosen.jsp?nodeids=25949&topCids=1495258,1494171,1495064,1495130,1495285,&pageidx=
        load_chosen = re.search(r'data.:."(.*)".+.masonry',html)
        page = 2
        tp_url = ""
        if load_chosen :
            tp_url = "http://www.thepaper.cn/load_chosen.jsp?%s%s&lastTime=%s" % (load_chosen.group(1),page,lasttime)
            yield scrapy.Request(tp_url, callback=self.next_page_parse)



    def next_page_parse(self,response):
        html = response.body
        url = response.url
        np_soup = BeautifulSoup(html,"lxml")
        #格式：<div id="last2" lastTime="1467972702826" pageIndex="2" style="display:none;"></div>
        res = np_soup.find(name="div",attrs={"lasttime":True})
        if res:
            lasttime = res.get("lasttime",None)
            pageindex = res.get("pageindex",None)

            if lasttime and pageindex:
                #终止条件，需更改，暂定前5页
                # if int(pageindex) <8:
                    pageindex = str(int(pageindex)+1)
                    new_url = re.sub(r'pageidx=.*?&lastTime=.*',"pageidx=%s&lastTime=%s" % (pageindex,lasttime),url,1)
                    yield scrapy.Request(new_url, callback=self.next_page_parse)
            # else:
                #log.msg("can't find lasttime or pageindex", level=log.INFO)

        for i in self.fetch_newslist(np_soup):
            if i['time'] == u"1天前": raise CloseSpider("today news end")
            yield i

    def fetch_newslist(self,soup):
        #爬取新闻链接
        news_list = soup.select('div[class="news_li"]')
        res=[]
        for news in news_list:
            if news.has_attr("lasttime"):break  #首页出现的特殊异常
            item = NewsItem()
            item["title"] = news.h2.a.string    #题目
            item["news_url"] = self.domain+news.h2.a.get("href") #新闻链接
            item["content"] = news.p.string     #简介
            item["pic"] = news.img.get("src")   #图片链接
            topic = news.select('div[class="pdtt_trbs"]')
            if topic:
                item["topic"] = topic[0].a.string  #专题
                item["time"]=topic[0].span.string  #对比爬取时间的时间
            res.append(item)
        return res
