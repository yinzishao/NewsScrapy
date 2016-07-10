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

class NewsItem(scrapy.Item):
    title = scrapy.Field()
    news_url = scrapy.Field()
    content = scrapy.Field()
    pic = scrapy.Field()
    topic = scrapy.Field()
    time = scrapy.Field()
    tags = scrapy.Field()