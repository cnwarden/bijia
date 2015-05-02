# coding:utf-8
#!/usr/bin/python

import sys
import pymongo
import getopt


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

    def deleteDB(self):
        self.client.drop_database("jd")

    def close(self):
        self.client.close()

def main():
    db = DBInit()
    try:
        options,args = getopt.getopt(sys.argv[1:], "hcd", ["help","category","delete_db"])
        for name,value in options:
            if name in ("-h", "--help"):
                pass
            if name in ("-c", "--category"):
                db.initCategory()
            if name in ("-d", "--delete_db"):
                db.deleteDB()
    except getopt.GetoptError:
        sys.exit()
    finally:
        db.close()


if __name__ == "__main__":
    main()