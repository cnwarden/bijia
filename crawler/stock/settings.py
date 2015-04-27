# -*- coding: utf-8 -*-

# Scrapy settings for stocknews project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'stock'

SPIDER_MODULES = ['stock.spiders']
NEWSPIDER_MODULE = 'stock.spiders'

ITEM_PIPELINES = {
    'stock.pipelines.StockPipeline': 300,
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2371.0 Safari/537.36'

LOG_LEVEL = 'INFO'

MONGODB_SERVER = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_DB = 'jd'
MONGODB_COLLECTION = 'stocks'


JD_IMAGE_ENABLE = False
JD_IMAGE_PATH = '/workspace/bijia/static/img/'
