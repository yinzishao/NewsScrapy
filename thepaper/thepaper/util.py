#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'

import time
import datetime
from thepaper.settings import *
"""
    判断传入的时间是否是当天
    request：
        date    struct
"""
def judge_today(date):
    return date.tm_mday == time.localtime().tm_mday

def judge_news_crawl(item):
    """
    判断是否符合爬取的时间
    :param item:
    :return: item or None
    """
    news_date = item.get("news_date",None)
    if news_date:
        struct_date = datetime.datetime.strptime(news_date,"%Y-%m-%d %H:%M:%S")
        delta = END_NOW-struct_date
        if delta.days < END_DAY:
            return item
        else:
            return None
    return None