#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'
import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("TechwebSpider")
from thepaper.settings import *
from thepaper.util import judge_news_crawl

#TODO:referer_web
class TechwebSpider(scrapy.spiders.Spider):
    domain = "http://www.techweb.com.cn"
    name = "techweb"
    indexpage =1
    allowed_domains = ["techweb.com.cn",]
    news_next_url = "http://www.techweb.com.cn/news/list_%s.shtml"    #资讯模块
    yuanchuang_next_url = "http://www.techweb.com.cn/yuanchuang/list_%s.shtml"    #原创模块
    news_flag = 0
    yuanchuang_flag = 0
    start_urls = [
        news_next_url % 1,
        yuanchuang_next_url % 1,
    ]
    def parse(self, response):
        origin_url = response.url
        pageindex = re.search(r"list_(\d+?).shtml",origin_url).group(1) if re.search(r"list_(\d+?).shtml",origin_url) else None
        soup = BeautifulSoup(response.body,"lxml")
        news_list = soup.find_all("div",class_="con_one")
        for news in news_list:
            title = news.h2.get_text(strip=True)
            news_url = news.h2.a.get("href",None)
            news_no = re.search(r"/(\d+?).shtml",news_url).group(1) if re.search(r"/(\d+?).shtml",news_url) else None
            abstract = news.p.get_text(strip=True)
            pic = news.find("img").get("src",None) if news.find("img") else None
            tags_list = news.find("span",class_="tag")("a") if news.find("span",class_="tag") else None
            tags =  [i.text for i in tags_list] if tags_list else None
            catalogue = u"原创" if "yuanchuang" in origin_url else u"咨询"
            item = NewsItem(
                news_url=news_url,
                news_no=news_no,
                title=title,
                pic=pic,
                abstract=abstract,
                tags=tags,
                catalogue=catalogue
            )
            yield scrapy.Request(news_url,callback=self.parse_news,meta={"pageindex":pageindex,"item":item})
        news_next_url = self.news_next_url % str(int(pageindex)+1)
        if "yuanchuang" in origin_url:
            if not self.yuanchuang_flag:
                yield scrapy.Request(news_next_url)
        else:
            if not self.news_flag:
                yield scrapy.Request(news_next_url)
    def parse_news(self,response):
        soup = BeautifulSoup(response.body,"lxml")
        origin_url  = response.url
        item = response.meta.get("item",NewsItem())
        news_index = response.meta.get("news_index",1)#新闻当前页数
        pageindex = response.meta.get("pageindex",1)#新闻爬取到的页数
        #新闻第一页，可能有下一页
        if news_index == 1:
            # if soup.find("span",class_="date") == None:
            #     import pdb;pdb.set_trace()
            news_date = soup.find("span",class_="date").get_text(strip=True) if soup.find("span",class_="date") else None
            #2016.07.28 22:12:52
            struct_date = datetime.datetime.strptime(news_date,"%Y.%m.%d %H:%M:%S")
            news_date = struct_date.strftime("%Y-%m-%d %H:%M:%S")
            # u''
            comment_text = soup.find("span",id="comment_num").text if soup.find("span",id="comment_num") else None
            if comment_text == u'':
                comment_num = 0
            else:
                comment_num = int(comment_text)

            #正文会有下一页 TODO:正文有js，需要替换。
            content_txt = soup.find("div",class_="content_txt")
            content = content_txt.get_text(strip=True) if content_txt else None
            referer_web = soup.find("span",id="source_baidu").a.get_text(strip=True) if soup.find("span",id="source_baidu") else None
            referer_url = soup.find("span",id="source_baidu").a.get("href") if soup.find("span",id="source_baidu") else None
            item["content"] = content
            item["news_date"] =news_date
            item["comment_num"] =comment_num
            item["crawl_date"] =NOW
            item["referer_web"] =referer_web
            item["referer_url"] =referer_url
            catalogue = item["catalogue"]
            item = judge_news_crawl(item)
            if item:
                if u"下一页" in content_txt.find("div",class_="page").text:
                #替换成下一页 格式：http://www.techweb.com.cn/world/2016-07-26/2365804_2.shtml


                    news_next_page = str(int(news_index)+1)
                    news_next_url = re.sub(r'\.shtml','_%s.shtml' % news_next_page,origin_url)
                    yield scrapy.Request(news_next_url,callback=self.parse_news,meta={"news_index":news_next_page,"item":item})
                else:
                    yield item
            else:
                if "原创".decode("utf-8") == catalogue:
                    self.yuanchuang_flag=pageindex
                else:
                    self.news_flag=pageindex
        #新闻的下一页
        else:
            content_txt = soup.find("div",class_="content_txt")
            content = content_txt.get_text(strip=True)
            item["content"] += u"\n第%s页\n%s" % (news_index,content)
            if item:
                #下一页是disabled说明没有下一页
                if not content_txt.find("div",class_="page").find("span",class_="disabled"):
                #替换成下一页 格式：http://www.techweb.com.cn/world/2016-07-26/2365804_2.shtml
                    news_next_url = re.sub(r'_.+?\.shtml','_%s.shtml' % str(int(news_index)+1),origin_url)
                    yield scrapy.Request(news_next_url,callback=self.parse_news,meta={"pageindex":str(int(news_index)+1),"item":item})
                else:
                    yield item




