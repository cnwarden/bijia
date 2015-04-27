from django.db import models
from mongoengine import *

# Create your models here.

class PriceList(EmbeddedDocument):
    price = StringField()
    time = StringField()

class Stock(Document):
    uid = IntField(required=True)
    name = StringField(max_length=200, required=True)
    url = StringField(max_length=200, required=True)
    comments = IntField(required=True)
    price_list = ListField(EmbeddedDocumentField(PriceList))

    meta = {'collection' : 'stocks'}


