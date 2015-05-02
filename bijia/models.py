from django.db import models
from mongoengine import *

# Create your models here.

class PriceList(EmbeddedDocument):
    price = StringField()
    time = DateTimeField()

class MobilePriceList(EmbeddedDocument):
    price = StringField()
    time = DateTimeField()

class Degree(EmbeddedDocument):
    predict_price = FloatField()
    value = FloatField()
    scope = IntField()
    change_time = DateTimeField()

class Stock(Document):
    uid = IntField(required=True)
    name = StringField(max_length=200, required=True)
    url = StringField(max_length=200, required=True)
    comments = IntField(required=True)
    category = IntField(required=True)
    changed = IntField()
    create_time = DateTimeField()
    last_update = StringField()
    last_price = FloatField()
    last_mobile_price = FloatField()
    degree = EmbeddedDocumentField(Degree)
    price_list = ListField(EmbeddedDocumentField(PriceList))
    mobile_price_list = ListField(EmbeddedDocumentField(MobilePriceList))

    meta = {'collection' : 'stocks'}

class Category(Document):
    name = StringField(max_length=200, required=True)
    value = IntField(required=True)

    meta = {'collection' : 'category'}


