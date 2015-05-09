import scrapy
import re
import codecs
from stock.settings import *
from stock.items import JDStockItem, JDStockPrice, JDStockMobilePrice, JDStockImage, JDStockPromotion, JDStockPromotionList
from scrapy.http import Request
from scrapy.log import INFO
from datetime import datetime
from json.decoder import JSONDecoder
from scrapy.conf import settings
from scrapy.log import msg
import os
from pymongo import MongoClient

PRICE_BASE_URL = 'http://p.3.cn/prices/get?skuid='

PRIORITY_PAGE = 1000
PRIORITY_PRICE = 500
PRIORITY_MOBILE_PRICE = 200
PRIORITY_PROMOTION_PRICE = 150

class JDSpider(scrapy.Spider):
    name = "jd_web"
    start_urls = []

    def __init__(self, category=None, *args, **kwargs):
        super(JDSpider, self).__init__(*args, **kwargs)

        self.log(category, INFO)
        for url in self.generate_root_url_by_configuration():
            self.start_urls.append(url)
        self.category = category

    def generate_root_url_by_configuration(self):
        self.client = MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        self.db = self.client[settings['MONGODB_DB']]
        self.collection = self.db['category']

        items = self.collection.aggregate([
            {"$unwind":"$provider"},
            {"$match":{"provider.name":"jd"}},
            {"$group": {
                "_id":"$_id",
                "name": {'$first': '$name'},
                "value": {'$first': '$value'},
                "param1": {'$first': '$provider.param1'},
            }}
        ])

        self.category_mapping = {}
        for item in items['result']:
            self.category_mapping[item['param1']] = int(item['value'])
            yield "http://list.jd.com/list.html?cat=%s&page=1&&delivery=1&JL=6_0_0" % (item["param1"])

    def get_category(self, provider_category):
        """
        convert jd category to standard category
        :return: the value of standard category
        """
        return self.category_mapping[provider_category]

    def make_requests_from_url(self, url):
        m = re.search('cat=(.*?)&', url)
        return Request(url, dont_filter=True, meta={'stock_page':1, 'category' : m.group(1)})

    def extract_single_stock(self, node):
        #price_class = node.xpath('.//div[@class="p-price"]/strong/@class').extract()[0]
        url = node.xpath('.//div[@class="p-name"]/a/@href').extract()[0]
        name = node.xpath('.//div[@class="p-name"]/a/@title').extract()[0]
        img = node.xpath('.//div[@class="p-img"]/a/img/@data-lazy-img').extract()[0]
        comments = node.xpath('.//div[@class="p-commit"]//a/text()').extract()[0]
        # remove the prefix J_
        id = url[url.rfind("/")+1 : url.rfind(".html")]
        #self.log("%s-%s-%s" % (id, url, name), INFO)

        return (id, name, url, img, comments)

    def generate_price_query_url(self, stock_id):
        return 'http://p.3.cn/prices/get?skuid=J_%s' % (stock_id)

    def generate_mobile_price_query_url(self, stock_id):
        return 'http://item.m.jd.com/product/%s.html' % (stock_id)

    def generate_promotion_query_url(self, stock_id):
        return 'http://pi.3.cn/promoinfo/get?id=%s&origin=1&callback=Promotions.set' % (stock_id)

    def generate_item(self, stock, category):
        item = JDStockItem()
        item['uid'] = int(stock[0])
        item['name'] = stock[1]
        item['url'] = stock[2]
        item['comments'] = int(stock[4])
        item['category'] = self.get_category(category)
        item['changed'] = 0
        item['last_update'] = datetime.now()
        item['last_price'] = float(0.0)
        item['last_mobile_price'] = float(0.0)
        return item

    def generate_price_item(self, price):
        item = JDStockPrice()
        item['uid'] = int(price[0])
        item['price'] = round(float(price[1]), 2)
        item['timestamp'] = datetime.now()
        return item

    def generate_mobile_price_item(self, uid, price):
        item = JDStockMobilePrice()
        item['uid'] = int(uid)
        try:
            item['mobile_price'] = round(float(price), 2)
        except UnicodeEncodeError:
            self.log("UnicodeEncodeError-->SKU:%s mobile price %s can't decode" % (uid, price))
            item['mobile_price'] = -1.00
        item['timestamp'] = datetime.now()
        return item

    def generate_img_item(self, image):
        item = JDStockImage()
        item['uid'] = int(image[0])
        item['data'] = image[3]
        return item

    def is_stock_img_exist(self, uid):
        return os.path.exists(os.path.join(settings['JD_IMAGE_PATH'], '%s.jpg' % (uid)))

    def parse(self, response):
        # Get price of item
        if(response.meta.has_key('stock_price')):
            price_obj = JSONDecoder().decode(response.body)
            #remove the prefix J_
            stock_id_str = price_obj[0]['id'][2:]
            yield self.generate_price_item((stock_id_str, price_obj[0]['p']))
            yield Request(url=self.generate_mobile_price_query_url(stock_id_str),
                    meta={'stock_mobile_price':1, 'stock_id':stock_id_str}, priority=PRIORITY_MOBILE_PRICE)
            return

        if(response.meta.has_key('stock_mobile_price')):
            m_price = response.xpath('//span[@class="p-price"]/text()').extract()[0][1:]

            yield self.generate_mobile_price_item(response.meta['stock_id'], m_price);
            yield Request(url=self.generate_promotion_query_url(response.meta['stock_id']),
                    meta={'stock_promotion':1, 'stock_id':response.meta['stock_id']}, priority=PRIORITY_PROMOTION_PRICE)

        if(response.meta.has_key('stock_img')):
            item = JDStockImage()
            item['uid'] = int(response.meta['stock_id'])
            item['data'] = response.body
            yield item
            return

        if(response.meta.has_key('stock_promotion')):
            itemList = JDStockPromotionList()
            itemList['uid'] = int(response.meta['stock_id'])
            itemList['promotionList'] = []

            m = re.match('Promotions.set\((.*)\);', response.body)
            if m:
                content = m.group(1)
                if content != "":
                    promotion_obj = JSONDecoder().decode(content)
                    promotionInfoList = promotion_obj['promotionInfoList']
                    if promotionInfoList:
                        for promotion in promotionInfoList:
                            if promotion['rebate']:
                                item = JDStockPromotion()
                                item['rebate'] = promotion['rebate']
                                itemList['promotionList'].append(item)
            yield itemList
            return

        if(response.meta.has_key('stock_page')):
            for stock in response.xpath('//li[@index]'):
                stock_tab_items = stock.xpath('.//div[contains(@class, "tab-content-item")]')
                if stock_tab_items:
                    for single_item in stock_tab_items:
                        item = self.extract_single_stock(single_item)
                        yield self.generate_item(item, response.meta['category'])
                        if not self.is_stock_img_exist(item[0]):
                            yield Request(url=item[3], meta={'stock_img':1, 'stock_id':item[0]})
                        yield Request(url=self.generate_price_query_url(item[0]), priority=PRIORITY_PRICE,
                                  meta={'stock_price':1})
                else:
                    item = self.extract_single_stock(stock)
                    yield self.generate_item(item, response.meta['category'])
                    if not self.is_stock_img_exist(item[0]):
                        yield Request(url=item[3], meta={'stock_img':1, 'stock_id':item[0]})
                    yield Request(url=self.generate_price_query_url(item[0]), priority=PRIORITY_PRICE,
                                  meta={'stock_price':1})

            next_page_nodes = response.xpath('//a[@class="pn-next"]')
            if next_page_nodes:
                next_page = next_page_nodes[0].xpath('@href').extract()[0]
                next_page_url = "http://list.jd.com%s" % (next_page)
                #self.log(next_page_url, INFO)
                r = Request(url=next_page_url, priority=PRIORITY_PAGE,
                            meta={'stock_page':1, 'category' : response.meta['category']})
                yield  r
            return
