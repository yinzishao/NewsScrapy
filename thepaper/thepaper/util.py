#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'yinzishao'

import time
"""
    判断传入的时间是否是当天
    request：
        date    struct
"""
def judge_today(date):
    return date.tm_mday == time.localtime().tm_mday