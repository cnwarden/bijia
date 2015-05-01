# coding:utf-8
#!/usr/bin/python

import pymongo


class DBInit(object):
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1',27017)
        self.db = self.client['jd']

    def initCategory(self):
        self.collection = self.db['category']

        items = [ {"name":'平板电视', "value" : 1},
                  {"name":'电饭煲',   "value" : 2},
                  {"name":'胎压监测', "value" : 3},
                ]

        for item in items:
            result = self.collection.find_one({'value':item['value']})
            if not result:
                self.collection.insert(item)

def main():
    db = DBInit()
    db.initCategory()


main()