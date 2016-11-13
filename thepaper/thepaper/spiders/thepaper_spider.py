#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
from scrapy.exceptions import CloseSpider
from thepaper.util import judge_news_crawl

__author__ = 'yinzishao'

import scrapy
from bs4 import BeautifulSoup
import re
from thepaper.items import NewsItem
import logging
from thepaper.settings import *
logger = logging.getLogger("ThepaperSpider")
class ThepaperSpider(scrapy.spiders.Spider):
    domain = "http://www.thepaper.cn/"
    name = "thepaper"
    allowed_domains = ["thepaper.cn"]
    end_day = END_DAY
    end_now = END_NOW
    flag = 0
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
            # if i['time'] == "一天前": raise CloseSpider("today news end")
            request = scrapy.Request(i['news_url'],callback=self.parse_news)
            request.meta['item'] = i
            request.meta['pageindex'] = 1
            yield request

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
        if load_chosen :
            tp_url = "http://www.thepaper.cn/load_chosen.jsp?%s%s&lastTime=%s" % (load_chosen.group(1),page,lasttime)
            yield scrapy.Request(tp_url, callback=self.next_page_parse)



    def next_page_parse(self,response):
        html = response.body
        url = response.url
        np_soup = BeautifulSoup(html,"lxml")
        #格式：<div id="last2" lastTime="1467972702826" pageIndex="2" style="display:none;"></div>
        res = np_soup.find(name="div",attrs={"lasttime":True})

        lasttime = res.get("lasttime",None) if res else None
        pageindex = res.get("pageindex",None)if res else None
        for i in self.fetch_newslist(np_soup):
            request = scrapy.Request(i['news_url'],callback=self.parse_news)
            request.meta['item'] = i
            request.meta["pageindex"] = i
            yield request
        #终结条件
        if not self.flag and lasttime:
            pageindex = str(int(pageindex)+1)
            new_url = re.sub(r'pageidx=.*?&lastTime=.*',"pageidx=%s&lastTime=%s" % (pageindex,lasttime),url,1)
            yield scrapy.Request(new_url, callback=self.next_page_parse)
        # else:
            #log.msg("can't find lasttime or pageindex", level=log.INFO)


    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        pageindex = response.meta.get("pageindex",None)
        soup = BeautifulSoup(response.body, "lxml")
        #TODO：新闻列表中会有专题，里面没有新闻的内容。现在是抛弃！
        #爬取新闻
        news_txt=soup.find("div",class_="news_txt")
        if news_txt:
            content = news_txt.text
            news_about = soup.find("div",class_="news_about")
            #referer_web,news_date
            if news_about:
                referer_web = news_about.p.string
                news_date = news_about.p.next_sibling.next_sibling.text[0:16]
                struct_date = datetime.datetime.strptime(news_date,"%Y-%m-%d %H:%M")
                news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
                item["referer_web"]=referer_web
                item["news_date"]=news_date
                item["content"]=content
                item["crawl_date"]=NOW
                # import pdb;pdb.set_trace()
                item = judge_news_crawl(item)
                if item:
                    yield item
                else:
                    self.flag = pageindex

        else:

            logger.info("news page can't find news_txt.That may be a theme")



    def fetch_newslist(self,soup):
        #爬取新闻链接
        news_list = soup.select('div[class="news_li"]')
        res=[]
        for news in news_list:
            if news.has_attr("lasttime"):break  #首页出现的特殊异常
            item = NewsItem()
            item["catalogue"] = "精选内容"      #目录
            item["title"] = news.h2.a.string    #题目
            item["news_url"] = self.domain+news.h2.a.get("href") #新闻链接
            item["abstract"] = news.p.string     #简介
            item["pic"] = news.img.get("src")   #图片链接
            topic = news.select('div[class="pdtt_trbs"]')
            if topic:
                item["topic"] = topic[0].a.string  #专题
                # item["time"]=topic[0].span.string  #对比爬取时间的时间
            news_no = news.find('a',class_="tiptitleImg").get("data-id",None)
            item['news_no']=news_no
            item['comment_num'] = news.find("span",class_="trbszan").string if news.find("span",class_="trbszan") else None
            res.append(item)

        return res
