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

class CarnocSpider(scrapy.spiders.Spider):
    domain = "http://news.carnoc.com/"
    name = "carnoc"
    allowed_domains = ["news.carnoc.com",]
    flag = 0
    start_urls = [
        "http://news.carnoc.com/cache/list/news_hotlist_1.html",
        "http://news.carnoc.com/cache/list/news_intelist_1.html",
        "http://news.carnoc.com/cache/list/news_gatlist_1.html",
        "http://news.carnoc.com/cache/list/news_sub1list_1_1.html",
        "http://news.carnoc.com/cache/list/news_sub1list_11_1.html",
        "http://news.carnoc.com/cache/list/news_sub1list_13_1.html",
        "http://news.carnoc.com/cache/list/news_sub1list_3_1.html",
        "http://news.carnoc.com/cache/list/news_sub1list_8_1.html",
        "http://news.carnoc.com/cache/list/news_sub1list_15_1.html"
    ]

    def parse(self,response):
        origin_url = response.url
        pageindex = int(origin_url.rsplit("_",1)[1].replace('.html',''))
        catalogue = re.search('</a> -&gt; ([\w\W]?) </i></h3>',response.body).group(1).decode("gb2312")
        soup = BeautifulSoup(response.body,"lxml")
        news_list = soup.find_all('li')
        for news in news_list:
            news_date = news.find('i').text.split(' ')[1].replace(']','') if news.find('i') else None
            if news_date:
                news_url = news.find('a',href = re.compile('http://news.carnoc.com/list/*.?')).get('href')
                news_no = news_url.rsplit('/',1)[1].replace('.html','')
                title = news.find('a',href = re.compile('http://news.carnoc.com/list/*.?')).text.strip()
                abstract = news.find('div').text.strip()
                pic = news.find('div').find('img',src = re.compile('http://pic.carnoc.com/file/*.?')).get('src') if news.find('div').find('img',src = re.compile('http://pic.carnoc.com/file/*.?')) else None
                tags = news.find('div',class_ = 'keywordslist').text.strip()
                item = NewsItem(
                    news_date = news_date + ' 00:00:00',
                    title = title,
                    abstract = abstract,
                    news_no = news_no,
                    catalogue = catalogue,
                    pic = pic,
                    tags = tags,
                    topic = None
                )
                item = judge_news_crawl(item)
                if item:
                    yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={'item':item})
                else:
                    self.flag = pageindex
            else:
                logger.warning("carnoc:%s can't find news_date " % origin_url)
        if not self.flag:
            next_url = origin_url.rsplit("_",1)[-1] + '_' + str(pageindex + 1) + '.html'
            yield scrapy.Request(next_url)

    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body)
        referer_web = soup.find('span',id='source_baidu').find('a').text.strip()
        referer_url = soup.find('span',id='source_baidu').find('a').get('href')
        author = soup.find('span',id='author_baidu').find('a').text.strip()
        crawl_date = NOW
        news_date = soup.find('span',id='pubtime_baidu').text.strip()
        comment_num = soup.find('span',class_ = 'pltit').find('b').text.strip()
        zan = soup.find('span',class_ = 'zan-plus').text.strip()
        read_num = int(comment_num) + int(zan)
        item['referer_web'] = referer_web
        item['referer_url'] = referer_url
        item['author'] = author
        item['crawl_date'] = crawl_date
        item['news_date'] = news_date
        item['comment_num'] = int(comment_num)
        item['read_num'] = read_num
        yield item
