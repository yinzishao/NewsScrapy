#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests

__author__ = 'yinzishao'

header={"Referer":"http://www.cb.com.cn/opinion/","User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0","Host":"www.cb.com.cn","Accept-Encoding":"gzip, deflate"}
cookie = dict(__jsl_clearance="1468945508.897|0|/uCuYHboSHAz2jbLhDkQSPPw+ck=",__jsluid="d9015b89c5a096f554ff4d78353a61ec")
r  = requests.get("http://www.cb.com.cn/opinion/",headers=header,cookies=cookie)
# print r.text
