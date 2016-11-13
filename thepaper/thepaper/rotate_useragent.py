#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64

__author__ = 'yinzishao'
# -*-coding:utf-8-*-

# from scrapy import log


"""避免被ban策略之一：使用useragent池。

使用注意：需在settings.py中进行相应的设置。
"""
import logging
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from settings import PROXIES,USER_AGENT_LIST
class RotateUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(USER_AGENT_LIST)
        if ua:
            #显示当前使用的useragent
            # print "********Current UserAgent:%s************" %ua

            #记录
            logger = logging.getLogger('USerAgent')
            logger.debug('Current UserAgent:%s' % ua)
            #旧版
            # log.msg('Current UserAgent: '+ua, level='INFO')
            request.headers.setdefault('User-Agent', ua)

    #the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    #for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        proxy = random.choice(PROXIES)
        if proxy['user_pass'] is not None:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
            encoded_user_pass = base64.encodestring(proxy['user_pass'])
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
            print "**************ProxyMiddleware have pass************" + proxy['ip_port']
        else:
            print "**************ProxyMiddleware no pass************" + proxy['ip_port']
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
