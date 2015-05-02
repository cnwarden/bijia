
import unittest
import sys
import os
from datetime import datetime,timedelta
from scrapy.conf import settings
from pymongo import MongoClient

# add module in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from stock.pipelines import StockPipeline
from stock.items import JDStockItem, JDStockPrice, JDStockImage, JDStockPromotion

class PiplelineUnitTest(unittest.TestCase):

    def setUp(self):
        self.client = MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        self.client.drop_database(settings['MONGODB_DB'])
        self.db = self.client[settings['MONGODB_DB']]
        self.collection = self.db[settings['MONGODB_COLLECTION']]

        self.pipeline = StockPipeline()

    def __generate_mock_stock(self, uid):
        item = JDStockItem()
        item['uid'] = uid
        item['name'] = 'test stock-%d' % (uid)
        item['url'] = 'http://test/%d.html' % (uid)
        item['comments'] = uid*10
        item['category'] = 1
        item['changed'] = 0
        item['last_update'] = datetime.now()
        item['last_price'] = float(0.0)
        item['last_mobile_price'] = float(0.0)
        return item

    def __generate_mock_stock_price(self, uid, price, time):
        item = JDStockPrice()
        item['uid'] = uid
        item['price'] = price
        item['timestamp'] = time
        return item

    def __generate_mock_mobile_stock_price(self, uid, price, time):
        item = JDStockPromotion()
        item['uid'] = uid
        item['mobile_price'] = price
        item['timestamp'] = time
        return item

    def test_case_1_create_single_item(self):
        self.pipeline.process_item(self.__generate_mock_stock(1), None)

        result = self.collection.find_one({'uid': 1})
        self.assertEqual(result['uid'], 1)

    def test_case_2_update_last_price(self):
        now = datetime.now()

        self.pipeline.process_item(self.__generate_mock_stock(1), None)
        self.pipeline.process_item(self.__generate_mock_stock_price(1, 1000.0, now), None)

        result = self.collection.find_one({'uid': 1})
        self.assertEqual(result['last_price'], 1000)
        self.assertEqual(result['price_list'][-1]['price'], 1000)
        self.assertEqual(result['last_update'], now)

    def test_case_3_update_last_mobile_price_with_None(self):
        now = datetime.now()

        self.pipeline.process_item(self.__generate_mock_stock(1), None)
        self.pipeline.process_item(self.__generate_mock_stock_price(1, 1000.0, now), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, None, now+timedelta(seconds=5)), None) # with None
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, None, now+timedelta(seconds=10)), None) # with None

        result = self.collection.find_one({'uid': 1})
        self.assertEqual(result['last_mobile_price'], 1000)
        self.assertEqual(result['mobile_price_list'][-1]['price'], 1000)
        self.assertEqual(result['last_update'], now+timedelta(seconds=5))

    def test_case_4_update_last_mobile_price(self):
        now = datetime.now()

        self.pipeline.process_item(self.__generate_mock_stock(1), None)
        self.pipeline.process_item(self.__generate_mock_stock_price(1, 1000.0, now), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, 1000.0, now+timedelta(seconds=5)), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, 1000.0, now+timedelta(seconds=10)), None)

        result = self.collection.find_one({'uid': 1})
        self.assertEqual(result['last_mobile_price'], 1000)
        self.assertEqual(result['mobile_price_list'][-1]['price'], 1000)
        self.assertEqual(result['last_update'], now+timedelta(seconds=5))

    def test_case_5_update_last_mobile_price_changed(self):
        now = datetime.now()

        self.pipeline.process_item(self.__generate_mock_stock(1), None)
        self.pipeline.process_item(self.__generate_mock_stock_price(1, 1000.0, now), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, None, now+timedelta(seconds=5)), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, 1010.0, now+timedelta(seconds=10)), None)

        result = self.collection.find_one({'uid': 1})
        self.assertEqual(result['last_mobile_price'], 1010)
        self.assertEqual(result['mobile_price_list'][-1]['price'], 1010)
        self.assertEqual(result['last_update'], now+timedelta(seconds=10))

    def test_case_6_update_last_mobile_price_changed_back(self):
        now = datetime.now()

        self.pipeline.process_item(self.__generate_mock_stock(1), None)
        self.pipeline.process_item(self.__generate_mock_stock_price(1, 1000.0, now), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, None, now+timedelta(seconds=5)), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, 1010.0, now+timedelta(seconds=10)), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, None, now+timedelta(seconds=15)), None)

        result = self.collection.find_one({'uid': 1})
        self.assertEqual(result['last_mobile_price'], 1000)
        self.assertEqual(result['mobile_price_list'][-1]['price'], 1000)
        self.assertEqual(result['last_update'], now+timedelta(seconds=15))

    def test_case_7_trigger_degree_calculate(self):
        now = datetime.now()

        self.pipeline.process_item(self.__generate_mock_stock(1), None)
        self.pipeline.process_item(self.__generate_mock_stock_price(1, 1000.0, now), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, None, now+timedelta(seconds=5)), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, 1010.0, now+timedelta(seconds=10)), None)

        result = self.collection.find_one({'uid': 1})
        self.assertEqual(result['degree']['value'], -10.0)
        self.assertEqual(result['degree']['change_time'], now+timedelta(seconds=10))

    def test_case_8_trigger_degree_calculate_back(self):
        now = datetime.now()

        self.pipeline.process_item(self.__generate_mock_stock(1), None)
        self.pipeline.process_item(self.__generate_mock_stock_price(1, 1000.0, now), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, None, now+timedelta(seconds=5)), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, 1010.0, now+timedelta(seconds=10)), None)
        self.pipeline.process_item(self.__generate_mock_mobile_stock_price(1, None, now+timedelta(seconds=15)), None)

        result = self.collection.find_one({'uid': 1})
        self.assertEqual(result['degree']['value'], 0)
        self.assertEqual(result['degree']['change_time'], now+timedelta(seconds=15))

    def tearDown(self):
        self.client.close()
        pass


if __name__ == '__main__':
    unittest.main()