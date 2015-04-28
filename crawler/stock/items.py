# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class JDStockItem(scrapy.Item):
    uid = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    comments = scrapy.Field()
    create_time = scrapy.Field()
    changed = scrapy.Field()
    last_update = scrapy.Field()

class JDStockPrice(scrapy.Item):
    uid = scrapy.Field()
    price = scrapy.Field()
    timestamp = scrapy.Field()

class JDStockImage(scrapy.Item):
    uid = scrapy.Field()
    data = scrapy.Field()
