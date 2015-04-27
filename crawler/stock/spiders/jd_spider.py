import scrapy
import re
import codecs
from stock.settings import *
from stock.items import JDStockItem, JDStockPrice, JDStockImage
from scrapy.http import Request
from scrapy.log import INFO
from datetime import datetime
from json.decoder import JSONDecoder
from scrapy.conf import settings

PRICE_BASE_URL = 'http://p.3.cn/prices/get?skuid='

class JDSpider(scrapy.Spider):
    name = "jd_web"
    start_urls = []

    def __init__(self, category=None, *args, **kwargs):
        super(JDSpider, self).__init__(*args, **kwargs)
        
        self.log(category, INFO)
        self.start_urls.append('http://list.jd.com/list.html?cat=%s&page=1&&delivery=1&JL=6_0_0' % (category))

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
        return 'http://p.3.cn/prices/get?skuid=J_' + stock_id

    def generate_item(self, stock):
        item = JDStockItem()
        item['uid'] = int(stock[0])
        item['name'] = stock[1]
        item['url'] = stock[2]
        item['comments'] = int(stock[4])
        return item

    def generate_price_item(self, price):
        item = JDStockPrice()
        item['uid'] = int(price[0])
        item['price'] = price[1]
        item['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return item

    def generate_img_item(self, image):
        item = JDStockImage()
        item['uid'] = int(image[0])
        item['data'] = image[3]
        return item

    def parse(self, response):
        # Get price of item
        if(response.headers["Content-Type"] == "application/json"):
            price_obj = JSONDecoder().decode(response.body)
            #remove the prefix J_
            yield self.generate_price_item((price_obj[0]['id'][2:], price_obj[0]['p']))
            return

        if(response.meta.has_key('stock_img')):
            item = JDStockImage()
            item['uid'] = int(response.meta['stock_id'])
            item['data'] = response.body
            yield item
            return

        for stock in response.xpath('//li[@index]'):
            stock_tab_items = stock.xpath('.//div[contains(@class, "tab-content-item")]')
            if stock_tab_items:
                for single_item in stock_tab_items:
                    item = self.extract_single_stock(single_item)
                    yield self.generate_item(item)
                    if settings['JD_IMAGE_ENABLE']:
                        yield Request(url=item[3], meta={'stock_img':1, 'stock_id':item[0]})
                    yield Request(url=self.generate_price_query_url(item[0]))
            else:
                item = self.extract_single_stock(stock)
                yield self.generate_item(item)
                if settings['JD_IMAGE_ENABLE']:
                    yield Request(url=item[3], meta={'stock_img':1, 'stock_id':item[0]})
                yield Request(url=self.generate_price_query_url(item[0]))

        next_page_nodes = response.xpath('//a[@class="pn-next"]')
        if next_page_nodes:
            next_page = next_page_nodes[0].xpath('@href').extract()[0]
            next_page_url = "http://list.jd.com%s" % (next_page)
            #self.log(next_page_url, INFO)
            r = Request(url=next_page_url)
            yield  r
