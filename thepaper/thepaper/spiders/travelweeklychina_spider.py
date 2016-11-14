#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'
import re
from scrapy.exceptions import CloseSpider
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import NewsItem
import json
logger = logging.getLogger("TravelWeeklyChinaSpider")
from thepaper.settings import *

class TravelWeeklyChinaSpider(scrapy.spiders.Spider):
    domain = "http://travelweekly-china.com/"
    name = "twc"
    allowed_domains = ["travelweekly-china.com",]
    end_day = END_DAY     #终结天数
    end_now = END_NOW
    post_next_url = "http://travelweekly-china.com/Dyna.asmx/PageContentList"
    start_urls = [
        "http://travelweekly-china.com/",
    ]
    """
    因为需要爬12个类别的新闻。一起爬取的时候终止条件不应该有一个种类的新过了时间就停止。
    应该是12个类别的新闻都达到结束时间时，结束。
    而且因为是异步的。爬取一个页面的新闻会不按时间顺序爬取，所以我们对一个页面的所有新闻都爬取才结束。
    """
    flag = {}
    #根据首页的新闻类别爬取各个类别的url
    def parse(self, response):
        soup = BeautifulSoup(response.body,"lxml")
        menu = soup.find('div',id="channel---7",class_="channel")
        # """
        if menu:
            for topic in menu('ul'):
                topic_name = topic.li.a.string
                url = topic.find("a").get("href",None)
                if url:
                    topic_url = self.domain+url
                    self.flag.setdefault(url[1:],0)
                    yield scrapy.Request(topic_url,callback=self.parse_topic)
        # """
        # yield scrapy.Request("http://travelweekly-china.com/31774",callback=self.parse_topic)
    #根据每个类型的首页得到新闻json的接口与参数
    def parse_topic(self,response):
        """

        :param response:
        :return:抛出每个类型的第一页访问json

        爬取下一页的链接
        POST请求
        需要三个参数：
            PageKey
            WidgetId
            PageNumber
        """

        soup = BeautifulSoup(response.body,"lxml")
        next_obj = soup.find("a",class_="insert-more show-more")
        #如果有下一页
        if next_obj:
            next_pagekey = next_obj.get("_p",None)
            next_wid = next_obj.get("_wid",None)
            # next_num = next_obj.get("_n",None)
            next_num = 1
            post_data = {"req":
                             {
                                 "PageKey":next_pagekey,
                                 "WidgetId":next_wid,
                                 "PageNumber":next_num
                             }
                         }
            # print self.flag
            # print response.request.url,"----------------"
            #抛出每个类型的第一页访问json
            yield scrapy.Request(self.post_next_url,
                                 callback=self.parse_newslist_json,
                                 method="POST",
                                 headers={"Content-Type":"application/json"},
                                 body=json.dumps(post_data))
        else:
            #http://travelweekly-china.com/31781  只有一页！
            flag_id = response.url.split("/")[-1]
            self.flag[str(flag_id)]=1
            print flag_id,"stop ~~~~~~"
            logger.warning("can't find next page")
    #新闻列表
    def parse_newslist_json(self,response):
        # print response.url
        # if self.post_next_url == response.url:
        res = json.loads(response.body)['d']
        #需要替换<div>因为并没有</div>会影响beautifulsoup的加载！！！
        res = re.sub(re.compile(r'<div.*?>'),"",res)
        news_list = BeautifulSoup(res,"lxml").find_all("article")
        # else:
        #     soup = BeautifulSoup(response.body,"lxml")
        #     news_list = soup.find('div',class_="start-feed")('article')
        origin_post_data = json.loads(response.request.body)
        post_data = origin_post_data.get("req",None)
        if post_data:
            old_pagenumber = post_data['PageNumber']
            post_data.update({"PageNumber":str(int(old_pagenumber)+1)})

        #抛出新闻！
        if news_list:
            for news in news_list:
                title = news.span.a.string
                url = news.span.a.get("href",None)
                # 格式<p>u'XXXXX\xa0'<a>XX<\a><\p>
                # content = unicode(news.p).replace(u'\xa0', u'').replace("<p>","").replace("</p>","")
                #可以获取到p的内容
                #news.p ->  \u7cfb\u5217\u6d3b\u52a8\u3002...\xa0
                #TODO:没有replace(u'\xa0'),仍然不知出现编码问题的原因，暂不处理
                abstract = news.p.strings.next()

                if url:
                    #列表并没有时间，所以不能设定停止条件
                    # print self.domain+url,"request"
                    yield scrapy.Request(self.domain+url,
                                         callback=self.parse_news,
                                         meta={
                                             "topic_id":post_data["PageKey"],"PageNumber":old_pagenumber
                                            }
                                         )

        PageKey = post_data['PageKey']
        flag_id =str(int(PageKey)-40037910)

        #继续抛出下一页的条件：该类型的标志为0
        if not self.flag[flag_id]:
            # print flag_id,"要爬取下一页！",pagenumber
            yield scrapy.Request(self.post_next_url,
                                 callback=self.parse_newslist_json,
                                 method="POST",
                                 headers={"Content-Type":"application/json"},
                                 body=json.dumps(post_data))

    #异步并不按时间顺序！
    def parse_news(self,response):
        # print response.url,"response"
        PageKey = response.meta.get("topic_id")
        PageNumber =response.meta.get("PageNumber")
        flag_id =str(int(PageKey)-40037910)
        soup =BeautifulSoup(response.body,"lxml")
        #2016-07-13
        news_date = soup.find("time").text if soup.find("time") else None
        # print self.flag[flag_id],int(PageNumber)
        """
        条件是该类别标记（self.flag[flag_id]）是0爬取，说明还没有爬到过期的。
        爬取页面是该页的也继续爬取。因为一个页面的爬取顺序是异步的。
        self.flag[flag_id]=过期页数
        """
        if not self.flag[flag_id] or int(PageNumber)==self.flag[flag_id]:
            #，没有超出范围


            struct_date = datetime.datetime.strptime(news_date,"%Y-%m-%d")
            # print self.end_now,struct_date,"time"
            delta = self.end_now-struct_date
            # print delta.days,"delta day ~~~~~~~~~~~~~~~~"
            if delta.days > self.end_day:
                self.flag[str(flag_id)]=int(PageNumber)
                # print flag_id,"stop ~~~~~~"
                # raise CloseSpider('today scrapy end')
            else:

                head = soup.find("div",class_="post-head")
                topic,title,abstract=None,None,None
                if head:
                    topic = head.find("span",class_="category").text if head.find("span",class_="category") else None
                    title =head.find("h1",class_="h1").text if head.find("h1",class_="h1") else None
                    abstract = head.find("span",class_="kicker").text if head.find("span",class_="kicker") else None
                content = soup.find("div",class_="post-body clearfix").text if soup.find("div",class_="post-body clearfix") else None
                news_no = response.url.split("/")[-1].split("?")[0]
                #TODO 评论数量js渲染，未解决
                item = NewsItem(title=title,topic=topic,
                                abstract=abstract,news_date=news_date,
                                content=content,news_no=news_no
                                ,crawl_date=NOW,news_url=response.url,catalogue='新闻板块')
                yield item
