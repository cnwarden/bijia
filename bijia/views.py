# coding:utf-8

from django.shortcuts import render
from django.views.generic import ListView

from django.http import HttpResponse, Http404
from django.db.models import Q
# Create your views here.
from bijia.models import Stock, Category
from django.shortcuts import render_to_response
from datetime import datetime

def stocklistview(request):
    provider = request.GET.get('provider', 'jd')
    category = request.GET.get('category', '1')
    display_method = request.GET.get('show', '1')
    stocks = None

    # read db categories
    categories = Category.objects.all()

    if provider == 'jd':
        if display_method == '1':
            #我看你最值
            stocks = Stock.objects.exclude('price_list').filter(category=category).order_by('-degree.value')[0:20]
        elif display_method == '2':
            #所有商品
            stocks = Stock.objects.filter(category=category).order_by('-last_price')[0:20]
        elif display_method == '3':
            #本日上新
            today = datetime.now().date()
            midnight = datetime(today.year, today.month, today.day)
            stocks = Stock.objects.filter(category=category).filter(create_time__gte=midnight).order_by('-create_time')[0:20]
            pass
        elif display_method == '4':
            #最新价格变动
            stocks = Stock.objects.filter(category=category).order_by('-degree.change_time')[0:20]
        elif display_method == '5':
            #移动好价
            stocks = Stock.objects.filter(category=category).where('this.last_price != this.last_mobile_price').order_by('-degree.change_time')[0:20]
        else:
            #所有商品
            stocks = Stock.objects.all().order_by('-comments')[0:20]

        return render_to_response('stock_list.html',
                                  context={'stock_list' : stocks,
                                           'category_list' : categories,
                                           'provider' : 'jd',
                                           'category' : int(category),
                                           'display_method' : display_method
                                           })
    else:
        return render_to_response('base.html')
