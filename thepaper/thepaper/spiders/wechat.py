#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random

__author__ = 'yinzishao'

import re
import scrapy
from bs4 import BeautifulSoup
import logging
from thepaper.items import WechatItem
import json
import time
logger = logging.getLogger("wechat")
from thepaper.settings import *
from thepaper.util import judge_news_crawl

class WechatSpider(scrapy.spiders.Spider):
    """
    获取微信公众号的文章
    """
    name = "wechat"
    download_delay = 1
    def start_requests(self):
        for weixin_id in WECHAT_IDS[7:8]:
            url = "http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=y&_sug_type_=" % weixin_id
            print url
            time.sleep(random.randint(2,5))
            yield scrapy.Request(url, self.parse, meta= {"weixin_id":weixin_id})
    #TODO:BUG
    def parse(self, response):
        weixin_id = response.meta.get("weixin_id", None)
        soup = BeautifulSoup(response.body,"lxml")
        url = soup.find("a",uigs="main_toweixin_account_image_0").get("href")   #获得公众号的主页
        name =  soup.find("a",uigs="main_toweixin_account_name_0").text.strip()
        print url
        time.sleep(random.randint(2,5))
        yield scrapy.Request(url, callback=self.parse_index, meta={"name":name, "weixin_id": weixin_id})

    def parse_index(self, response):
        """
        获取公众号的文章列表
        :param response:    公众号主页
        :return:
        """
        weixin_id = response.meta.get("weixin_id", None)
        msg = re.search(r"var msgList =([\W\w]+?)seajs.use",response.body).group(1).strip()[:-1]  # 获得公众号的文章列表
        msg_dict = json.loads(msg)
        weixin_name = response.meta.get("name", None)
        article_list = []
        for u in msg_dict["list"]:
            news_date = u["comm_msg_info"]["datetime"]  #某天所有发布的文章的时间戳
            news_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(news_date)))  #时间转换
            title = u["app_msg_ext_info"]["title"] #某天最后跟新的文章的标题
            news_url = "http://mp.weixin.qq.com" + u["app_msg_ext_info"]["content_url"] #某天最后跟新的文章的url
            pic = u["app_msg_ext_info"]["cover"]    #某天最后跟新的文章的图片
            abstract = u["app_msg_ext_info"]["digest"] #某天最后跟新的文章的摘要
            author = u["app_msg_ext_info"]["author"] # 某天最后跟新的文章的作者
            fileid = u["app_msg_ext_info"]["fileid"] # 某天最后跟新的文章的fileid
            source_url = u["app_msg_ext_info"]["source_url"] # 某天最后跟新的文章的来源信息
            article = {"weixin_id":weixin_id,"weixin_name":weixin_name,"news_date":news_date,"title":title,"news_url":news_url.replace("&amp;","&"),"pic":pic,"abstract":abstract,"author":author,"fileid":fileid,"source_url":source_url}
            article_list.append(article)
            item = WechatItem(
                weixin_id = weixin_id,
                weixin_name = weixin_name,
                news_date = news_date,
                title = title,
                news_url = news_url.replace("&amp;","&"),
                pic = pic,
                abstract = abstract,
                author = author,
                fileid = fileid,
                source_url = source_url
            )
            item = judge_news_crawl(item)
            if item:
                time.sleep(random.randint(2,5))
                print item['news_url']
                yield scrapy.Request(item['news_url'],callback=self.parse_news, meta={"item": item})
            for c in u["app_msg_ext_info"]["multi_app_msg_item_list"]:
                title = c["title"] #某天的文章的标题
                news_url = "http://mp.weixin.qq.com" + c["content_url"] #某天的文章的url
                pic = c["cover"]    #某天的文章的图片
                abstract = c["digest"] #某天的文章的摘要
                author = c["author"] # 某天的文章的作者
                fileid = c["fileid"] # 某天的文章的fileid
                source_url = c["source_url"] # 某天的文章的来源url
                article = {"weixin_id":weixin_id,"weixin_name":weixin_name,"news_date":news_date,"title":title,"news_url":news_url.replace("&amp;","&"),"pic":pic,"abstract":abstract,"author":author,"fileid":fileid,"source_url":source_url}
                article_list.append(article)
                item = WechatItem(
                    weixin_id = weixin_id,
                    weixin_name = weixin_name,
                    news_date = news_date,
                    title = title,
                    news_url = news_url.replace("&amp;","&"),
                    pic = pic,
                    abstract = abstract,
                    author = author,
                    fileid = fileid,
                    source_url = source_url
                )
                item = judge_news_crawl(item)
                if item:
                    print item['news_url']
                    time.sleep(random.randint(2,5))
                    yield scrapy.Request(item['news_url'],callback=self.parse_news, meta={"item": item})

    def parse_news(self, response):
        item = response.meta.get('item', WechatItem())
        soup = BeautifulSoup(response.body,"lxml")
        item["content"] = soup.find_all('div',class_ = 'rich_media_content')[0].text.strip()
        yield item