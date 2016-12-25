#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'

import time
import datetime
from settings import *


with open("keywords.txt") as f : keywords  = [ line.strip().split(" ")[0].decode("utf-8") for line in f.readlines()]
f.close()
"""
    判断传入的时间是否是当天
    request：
        date    struct
"""
def judge_today(date):
    return date.tm_mday == time.localtime().tm_mday

def judge_news_crawl(item,end_day=END_DAY):
    """
    判断是否符合爬取的时间
    :param
    item:
    end_day:指定结束天数
    :return: item or None
    """
    news_date = item.get("news_date",None)
    if news_date:
        struct_date = datetime.datetime.strptime(news_date,"%Y-%m-%d %H:%M:%S")
        delta = END_NOW-struct_date
        if delta.days < end_day:
            return item
        else:
            return None
    return None

def judge_key_words(item):
    item_keywords = []
    title = item.get("title",None)
    content = item.get("content",None)
    if title:
        for w in keywords:
            if w in title:
                item_keywords.append(w)
    if content:
        for w in keywords:
            if w in content:
                item_keywords.append(w)
    if len(item_keywords) > 0:
        item_keywords = list(set(item_keywords))
        return item_keywords
    else:
        return None
