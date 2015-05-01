# -*- coding: utf-8 -*-

# Scrapy settings for stocknews project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import platform
import os

BOT_NAME = 'stock'

SPIDER_MODULES = ['stock.spiders']
NEWSPIDER_MODULE = 'stock.spiders'

ITEM_PIPELINES = {
    'stock.pipelines.StockPipeline': 300,
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2371.0 Safari/537.36'

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scrapy_crawl.log')
print LOG_FILE
LOG_LEVEL = 'INFO'

MONGODB_SERVER = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_DB = 'jd'
MONGODB_COLLECTION = 'stocks'

JD_IMAGE_PATH = '/workspace/bijia/static/img/'

if platform.system() == "Windows":
    JD_IMAGE_PATH = 'D:\\991_GitHub\\bijia\\static\\img'
