from django.shortcuts import render
from django.views.generic import ListView

from django.http import HttpResponse, Http404
# Create your views here.
from bijia.models import Stock
from django.shortcuts import render_to_response

def stocklistview(request):
    stocks = Stock.objects.order_by('-comments')[0:10]
    return render_to_response('stock_list.html', context={'stock_list' : stocks})
