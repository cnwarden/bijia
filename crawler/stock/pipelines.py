# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from pymongo import MongoClient

from scrapy.conf import settings
from scrapy.log import msg
from stock.items import JDStockItem, JDStockPrice, JDStockImage, JDStockPromotion
from datetime import datetime

class StockPipeline(object):

    def __init__(self):
        super(StockPipeline, self).__init__()

        self.client = MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        self.db = self.client[settings['MONGODB_DB']]
        self.collection = self.db[settings['MONGODB_COLLECTION']]

    def __evaluate(self):
        pass

    def __save_image(self, item):
        img_path = os.path.join(settings['JD_IMAGE_PATH'], str(item['uid']) + '.jpg')
        fp_img = open(img_path, 'wb')
        fp_img.write(item['data'])
        fp_img.close()

    def __create_or_update_stock(self, item):
        result = self.collection.find_one({'uid': item['uid']})
        if not result:
            item['create_time'] = datetime.now()
            item['degree'] = {'value':0.0, 'scope':0, 'change_time':datetime.now()}
            result = self.collection.insert(dict(item))
        else:
            result = self.collection.update({'uid': item['uid']}, {'$set':{'comments':item['comments']}})

    def __create_or_update_price(self, item):
        # update last update time
        result = self.collection.update({'uid': item['uid']},
                                        {'$set' : {'last_update': item['timestamp']}}, True)
        if result:
                result = self.collection.find_one({'uid': item['uid']})
                # update last change time
                if result['last_price'] != item['price']:
                    self.collection.update({'uid': item['uid']}, {'$set':{'degree.change_time' : datetime.now()}}, True)
                self.collection.update({'uid': item['uid']}, {'$set':{'last_price':item['price']}}, True)

                # check whether update price_list
                if result.has_key('price_list'):
                    if result['price_list'][-1]['price'] == item['price']:
                        pass
                    else:
                        result = self.collection.update({'uid': item['uid']}, {
                            '$push' : { 'price_list' :
                                { 'price':item['price'], 'time':item['timestamp'] } },
                            '$set'  : { 'changed' : 1 }
                            }, True)
                else:
                    # non-exist then update as default value
                    result = self.collection.update({'uid': item['uid']}, {
                        '$push' : { 'price_list' :
                            { 'price':item['price'], 'time':item['timestamp'] } },
                        '$set'  : { 'changed' : 0 }
                        }, True)

    def __update_with_promotion(self, item):
        # update snapshot price
        result = self.collection.find_one({'uid': item['uid']})
        if not item['mobile_price']:
            # first set or mobile price change back to normal price
            self.collection.update({'uid': item['uid']}, {'$set':{'last_mobile_price':result['last_price']}})
            result = self.collection.update({'uid': item['uid']}, {
                            '$push' : { 'mobile_price_list' :
                                    { 'price': result['last_price'], 'time':item['timestamp'] } },
                            }, True)
        else:
            msg('mobile->%d' % (item['uid']))
            # update last change time
            if result['last_mobile_price'] != item['mobile_price']:
                self.collection.update({'uid': item['uid']}, {'$set':{'degree.change_time' : datetime.now()}}, True)
            # promotion be after the price, set last price to correct one
            self.collection.update({'uid': item['uid']}, {'$set':{'last_mobile_price':item['mobile_price']}}, True)
            # update degree
            self.collection.update({'uid': item['uid']},
                                {'$set' :
                                     {
                                         'degree.value' : result['last_price'] - item['mobile_price'],
                                         'degree.scope' : 0
                                     }
                                 }, True)

            if result.has_key('mobile_price_list'):
                if result['mobile_price_list'][-1]['price'] == item['mobile_price']:
                    pass
                else:
                    result = self.collection.update({'uid': item['uid']}, {
                                '$push' : { 'mobile_price_list' :
                                        {'price':item['mobile_price'], 'time': item['timestamp'] }}
                                }, True)
            else:
                # non-exist then update as default value
                result = self.collection.update({'uid': item['uid']}, {
                        '$push' : { 'mobile_price_list' :
                            { 'price':item['mobile_price'], 'time':item['timestamp'] } },
                        }, True)

    def process_item(self, item, spider):
        if isinstance(item, JDStockPrice):
            self.__create_or_update_price(item)
        elif isinstance(item, JDStockPromotion):
            self.__update_with_promotion(item)
        elif isinstance(item, JDStockImage):
            self.__save_image(item)
        elif isinstance(item, JDStockItem):
            self.__create_or_update_stock(item)
        else:
            pass
        return item
