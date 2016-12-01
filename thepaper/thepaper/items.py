# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ThepaperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
"""
新闻(标题,摘要,正文,url,发布时间,爬从抓取的时间,引用的网站名,引用的源url,作者,已阅读量,已评论量,新闻图片,所在网站的新闻标号,所在网站所属目录)
"""
class NewsItem(scrapy.Item):
    _id = scrapy.Field()        #id
    title = scrapy.Field()      #标题
    abstract = scrapy.Field()   #摘要
    news_date = scrapy.Field()  #发布时间
    content = scrapy.Field()    #正文
    news_url = scrapy.Field()   #url
    crawl_date = scrapy.Field() #爬从抓取的时间
    referer_web = scrapy.Field()#引用的网站名
    referer_url = scrapy.Field()#引用的源url
    author = scrapy.Field()     #作者
    read_num = scrapy.Field()   #已阅读量
    comment_num =scrapy.Field() #已评论量
    pic = scrapy.Field()        #新闻图片
    news_no = scrapy.Field()    #所在网站新闻标号
    topic = scrapy.Field()      #所在网站所属主题
    catalogue = scrapy.Field()  #所在网站所属目录
    tags = scrapy.Field()       #标签
    keywords = scrapy.Field()   #找到对应的关键词
    source = scrapy.Field()     #来源网站(网易科技)

class WechatItem(scrapy.Item):
    _id = scrapy.Field()        #id
    title = scrapy.Field()      #标题
    abstract = scrapy.Field()   #摘要
    news_date = scrapy.Field()  #发布时间
    content = scrapy.Field()    #正文
    news_url = scrapy.Field()   #url
    crawl_date = scrapy.Field() #爬从抓取的时间
    referer_web = scrapy.Field()#引用的网站名
    referer_url = scrapy.Field()#引用的源url
    author = scrapy.Field()     #作者
    read_num = scrapy.Field()   #已阅读量
    comment_num =scrapy.Field() #已评论量
    pic = scrapy.Field()        #新闻图片
    news_no = scrapy.Field()    #所在网站新闻标号
    topic = scrapy.Field()      #所在网站所属主题
    catalogue = scrapy.Field()  #所在网站所属目录
    tags = scrapy.Field()       #标签
    keywords = scrapy.Field()   #找到对应的关键词
    source = scrapy.Field()     #来源网站(网易科技)
    weixin_id = scrapy.Field()  #微信Id
    weixin_name = scrapy.Field()#微信名
    source_url = scrapy.Field() #原链接
    fileid = scrapy.Field()     #文章的fileid