# coding:utf-8

from django.shortcuts import render
from django.views.generic import ListView

from django.http import HttpResponse, Http404
from django.db.models import Q
# Create your views here.
from bijia.models import Stock, Category
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime
import os

ITEMS_IN_SINGLE_PAGE = 20

def stocklistview(request):
    provider = request.GET.get('provider', 'jd')
    category = request.GET.get('category', '1')
    display_method = request.GET.get('show', '1')
    page = request.GET.get('page', 1)

    # read db categories
    categories = Category.objects.all()

    if provider == 'jd':
        if display_method == '1':
            #我看你最值
            stocks = Stock.objects.exclude('price_list').exclude('mobile_price_list').filter(category=category).order_by('-degree.value')
        elif display_method == '2':
            #所有商品
            stocks = Stock.objects.exclude('price_list').exclude('mobile_price_list').filter(category=category).order_by('-last_price')
        elif display_method == '3':
            #本日上新
            today = datetime.now().date()
            midnight = datetime(today.year, today.month, today.day)
            stocks = Stock.objects.exclude('price_list').exclude('mobile_price_list').filter(category=category).filter(create_time__gte=midnight).order_by('-create_time')
            pass
        elif display_method == '4':
            #最新价格变动
            stocks = Stock.objects.exclude('price_list').exclude('mobile_price_list').filter(category=category).order_by('-degree.change_time')
        elif display_method == '5':
            #移动好价
            stocks = Stock.objects.exclude('price_list').exclude('mobile_price_list').filter(category=category).where('this.last_price != this.last_mobile_price').order_by('-degree.change_time')
        else:
            #所有商品
            stocks = Stock.objects.exclude('price_list').exclude('mobile_price_list').order_by('-comments')

        p = Paginator(stocks, ITEMS_IN_SINGLE_PAGE)
        try:
            stocks_in_page = p.page(page)
        except PageNotAnInteger:
            stocks_in_page = p.page(1)
        except EmptyPage:
            stocks_in_page = p.page(p.num_pages)

        return render_to_response('stock_list.html',
                                  context={'stock_list' : stocks_in_page,
                                           'category_list' : categories,
                                           'provider' : 'jd',
                                           'category' : int(category),
                                           'display_method' : display_method
                                           })
    else:
        return render_to_response('base.html')


def addipview(request):
    serverip = request.GET.get('ip', '127.0.0.1')
    fp = open('hosts', 'w')
    fp.write(serverip)
    fp.close()
    return HttpResponse("<h1>%s</h1>" % (serverip))


def serverview(request):
    serverip = None
    if os.path.exists('hosts'):
        fp = open('hosts', 'r')
        serverip = fp.readline()
        fp.close()
    return HttpResponse("<h1>LINODE IP ADDRESS:%s</h1>" % (serverip))