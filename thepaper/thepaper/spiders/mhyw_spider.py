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


class MhywSpider(scrapy.spiders.Spider):
    domain = "http://www.caac.gov.cn"
    name = "mhyw"
    allowed_domains = ["caac.gov.cn",]
    next_url = "http://www.caac.gov.cn/XWZX/MHYW/index_%s.html"
    flag = 0
    start_urls = [
        "http://www.caac.gov.cn/XWZX/MHYW/",
    ]

    def parse(self,response):
        origin_url = response.url
        if 'index' not in origin_url:
            pageindex = 0
        else:
            pageindex = origin_url.rsplit('index_',1)[-1].replace('.html','')
            pageindex = int(pageindex)
        soup = BeautifulSoup(response.body.decode('utf8'),"lxml")
        news_list = soup.find_all('li',style = 'overflow:hidden;')
        for news in news_list:
            news_date = news.find('span').text if news.find('span') else None
            if news_date :
                news_url = news.find('a').get('href')
                news_no = news_url.rsplit('/',1)[-1].replace('.html','') # http://www.caac.gov.cn/XWZX/MHYW/201607/t20160726_39146.html
                title = news.find('a',href = re.compile('http://www.caac.gov.cn/XWZX/MHYW/')).text.strip() if news.find('a',href = re.compile('http://www.caac.gov.cn/XWZX/MHYW/')) else None
                item = NewsItem(
                    news_date = news_date + ' 00:00:00',
                    title = title,
                    news_url = news_url,
                    news_no = news_no
                )
                item = judge_news_crawl(item)
                if item:
                    yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={"item":item})
                else:
                    self.flag = pageindex
            else:
                logger.warning("mhyw can't find news_date")
        if not self.flag:
            next_url = self.next_url % (str(pageindex + 1 ))
            yield scrapy.Request(next_url)

    def parse_news(self,response):
        origin_url = response.url
        item = response.meta.get('item',NewsItem())
        if 'html' not in origin_url:
            yield item
        else:
            url_head = origin_url.rsplit('/',1)[0]
            soup = BeautifulSoup(response.body.decode('utf-8'))
            if soup.find('p',align="center") and soup.find('p',align="center").find('img'):
                pic = url_head + soup.find('p',align="center").find('img').get('src')[1:]
            else:
                pic = None
            referer_web = soup.find('span',class_ = 'p_r20').text.strip().split(u'：')[0]
            if soup.find('p',align="left"):
                abstract = soup.find('p',align="left").get_text(strip = True)
            else:
                abstract = None
            content = [ p.get_text(strip = True) for p in soup.find_all('p',align="justify")]
            content = '\n'.join(content)
            item['pic'] = pic
            item['referer_web'] = referer_web
            item['abstract'] = abstract
            item['content'] = content
            yield item