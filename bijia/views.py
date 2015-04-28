from django.shortcuts import render
from django.views.generic import ListView

from django.http import HttpResponse, Http404
# Create your views here.
from bijia.models import Stock
from django.shortcuts import render_to_response

def stocklistview(request):
    provider = request.GET.get('provider', 'jd')
    category = request.GET.get('category', 'tv')
    display_method = request.GET.get('show', '1')
    stocks = None
    if provider == 'jd':
        if display_method == '2':
            stocks = Stock.objects.filter(changed=1).order_by('last_update')[0:10]
        elif display_method == '3':
            stocks = Stock.objects.filter(changed=1).order_by('last_update')[0:10]
        elif display_method == '4':
            stocks = Stock.objects.filter(changed=1).order_by('last_update')[0:10]
        else:
            # show all
            stocks = Stock.objects.order_by('last_update')[0:10]
        return render_to_response('stock_list.html',
                                  context={'stock_list' : stocks,
                                           'provider' : 'jd',
                                           'category' : 'tv',
                                           })
    else:
        return render_to_response('base.html')
