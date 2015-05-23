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
from django.http import HttpResponseRedirect
import os, urllib, urllib2
from json import JSONDecoder
from appstore.settings import WEIBO_REDIRECT_URL

ITEMS_IN_SINGLE_PAGE = 20

APP_KEY = '433156516'
APP_SECRET = '73e92bf8321e5241d717735f30baa1f5'

def stocklistview(request):
    #user_info
    logined = request.session.get('logined', False)
    name = request.session.get('name', '')




    provider = request.GET.get('provider', 'jd')
    category = request.GET.get('category', '1')
    display_method = request.GET.get('show', '1')
    page = request.GET.get('page', 1)

    redirect_url = WEIBO_REDIRECT_URL

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
                                           'display_method' : display_method,

                                           'logined' : logined,
                                           'name' : name,
                                           'redirect_url' : redirect_url,
                                           })
    else:
        return render_to_response('base.html')

def weibologinview(request):
    if not request.session.get('logined', False):
        code = request.GET.get('code','')

        url = 'https://api.weibo.com/oauth2/access_token'

        data = {'client_id':APP_KEY,
                'client_secret':APP_SECRET,
                'grant_type':'authorization_code',
                'redirect_uri':WEIBO_REDIRECT_URL,
                'code':code}

        post_data = urllib.urlencode(data)

        req = urllib2.Request(url, data=post_data)
        req.add_header('Content-Type', "application/x-www-form-urlencoded")
        response = urllib2.urlopen(req)
        data = response.read()

        decoder = JSONDecoder().decode(data)
        access_token = decoder['access_token']
        expires_in = decoder['expires_in']
        remind_in = decoder['remind_in']
        uid = decoder['uid']

        user_info_url = 'https://api.weibo.com/2/users/show.json?source=%s&uid=%s&access_token=%s' % (APP_KEY, uid, access_token)
        req = urllib2.Request(user_info_url)
        try:
            res = urllib2.urlopen(req)
            data = res.read()
            user_data = JSONDecoder().decode(data)
            request.session['name'] = user_data['screen_name']
        except urllib2.HTTPError as ex:
            error = ex.read()
            print error

        request.session['logined'] = True
        request.session['token'] = access_token
        request.session['uid'] = uid
        return HttpResponseRedirect('/bijia/index')
    else:
        return HttpResponse("<h1>Logined</h1>")

def msgpostview(request):
    content = request.GET.get('content', '')

    if not content:
        return HttpResponse("<h1>无发布内容</h1>")

    post_url = 'https://api.weibo.com/2/statuses/update.json'

    if isinstance(content, unicode):
        content = content.encode('utf-8')

    data = {'source':APP_KEY,
            'access_token':request.session.get('token'),
            'status':content,
            }
    req = urllib2.Request(post_url)

    try:
        response = urllib2.urlopen(req, data = urllib.urlencode(data))
        return_data = response.read()
        resp_api = JSONDecoder().decode(return_data)
        return HttpResponse("<h1>%s</h1>" % (resp_api['created_at']))
    except urllib2.HTTPError as ex:
        print ex.read()
    return HttpResponse("<h1>发布失败</h1>")

def addipview(request):
    serverip = request.GET.get('ip', '127.0.0.1')
    fp = open('hosts', 'w')
    fp.write(serverip)
    fp.close()
    return HttpResponse("<h1>ADDED:%s</h1>" % (serverip))


def serverview(request):
    serverip = None
    if os.path.exists('hosts'):
        fp = open('hosts', 'r')
        serverip = fp.readline()
        fp.close()
    return HttpResponse("%s" % (serverip))