# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from pymongo import MongoClient

from scrapy.conf import settings
from stock.items import JDStockItem, JDStockPrice, JDStockImage

class StockPipeline(object):

    def __init__(self):
        super(StockPipeline, self).__init__()

        self.client = MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        self.db = self.client[settings['MONGODB_DB']]
        self.collection = self.db[settings['MONGODB_COLLECTION']]


    def process_item(self, item, spider):
        if isinstance(item, JDStockPrice):
            result = self.collection.update({'uid': item['uid']},
                                                {'$push' : { 'price_list' :
                                                     { 'price':item['price'], 'time':item['timestamp'] } }}, True)
        elif isinstance(item, JDStockImage):
            img_path = os.path.join(settings['JD_IMAGE_PATH'], str(item['uid']) + '.jpg')
            fp_img = open(img_path, 'wb')
            fp_img.write(item['data'])
            fp_img.close()
        elif isinstance(item, JDStockItem):
            result = self.collection.find_one({'uid': item['uid']})
            if not result:
                result = self.collection.insert(dict(item))
            else:
                result = self.collection.update({'uid': item['uid']}, {'$set':{'comments':item['comments']}})
        else:
            pass
        return item
