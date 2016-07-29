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


class Money163Spider(scrapy.spiders.Spider):
    domain = 'http://money.163.com/'
    name = 'money163'
    allowed_domains = ['money.163.com']
    next_url = 'http://money.163.com/special/002526O5/transport_%s.html'
    flag = 0
    start_urls = [
        'http://money.163.com/special/002526O5/transport.html'
    ]

    def parse(self,response):
        origin_url = response.url
        if '_' not in origin_url:
            pageindex = '1'
            origin_url = origin_url.rsplit('.',1)[0] + '_0' + '.html'
        else:
            pageindex = origin_url.rsplit('_',1)[-1].replace('.html','')
        soup = BeautifulSoup(response.body)
        catalogue = soup.find('div' ,class_ = 'nav_cur_index').find('span').text
        news_list = soup.find_all('div',class_ = 'item_top')
        for news in news_list:
            news_date = news.find('span',class_ = 'time').text.strip() if news.find('span',class_ = 'time') else None
            if news_date:
                news_url = news.find('h2').find('a',href = re.compile('http://money.163.com/')).get('href')
                title = news.find('h2').find('a',href = re.compile('http://money.163.com/')).text
                item = NewsItem(
                    news_date = news_date,
                    news_url = news_url,
                    title = title,
                    catalogue = catalogue
                )
                item = judge_news_crawl(item)
                if item:
                    yield scrapy.Request(item["news_url"],callback=self.parse_news,meta={'item':item})
                else:
                    self.flag = pageindex
            else:
                logger.warning("carnoc:%s can't find news_date " % origin_url)
        if not self.flag:
            pageindex = str(int(pageindex) + 1 ) if int(pageindex) > 9 else '0' + str(int(pageindex) + 1)
            next_url = self.next_url % (pageindex)
            yield scrapy.Request(next_url)

    def parse_news(self,response):
        item = response.meta.get("item",NewsItem())
        soup = BeautifulSoup(response.body.decode('gbk'))
        pic = soup.find('p' , class_ = 'f_center').find('img').get('src') if  soup.find('p' , class_ = 'f_center') and soup.find('p' , class_ = 'f_center').find('img') else None
        referer_web = soup.find('a',id = 'ne_article_source').text if soup.find('a',id = 'ne_article_source') else None
        referer_url = soup.find('a',id = 'ne_article_source').get('href') if soup.find('a',id = 'ne_article_source') else None
        author = soup.find('span',class_ = 'ep-editor').text if soup.find('span',class_ = 'ep-editor') else None
        if u"：" in author:
            author = author.split(u"：")[-1]
        crawl_date = NOW
        read_num = soup.find('div',class_ = 'post_comment_joincount').find('a').text if soup.find('div',class_ = 'post_comment_tiecount') else 0
        comment_num = soup.find('div',class_ = 'post_comment_tiecount').find('a').text if soup.find('div',class_ = 'post_comment_tiecount') else 0
        content = soup.find('div',class_ = 'post_text').get_text(strip=True) if soup.find('div',class_ = 'post_text') else None
        item['referer_web'] = referer_web
        item['content'] = content
        item['referer_url'] = referer_url
        item['author'] = author
        item['crawl_date'] = crawl_date
        item['pic'] = pic
        item['comment_num'] = int(comment_num)
        item['read_num'] = int(read_num)
        yield item