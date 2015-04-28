from django.shortcuts import render
from django.views.generic import ListView

from django.http import HttpResponse, Http404
# Create your views here.
from bijia.models import Stock, Category
from django.shortcuts import render_to_response

def stocklistview(request):
    provider = request.GET.get('provider', 'jd')
    category = request.GET.get('category', '1')
    display_method = request.GET.get('show', '1')
    stocks = None

    # read db categories
    categories = Category.objects.all()

    if provider == 'jd':
        if display_method == '2':
            stocks = Stock.objects.filter(category=category, changed=1).order_by('last_update')[0:10]
        elif display_method == '3':
            stocks = Stock.objects.filter(category=category, changed=1).order_by('last_update')[0:10]
        elif display_method == '4':
            stocks = Stock.objects.filter(category=category, changed=1).order_by('last_update')[0:10]
        else:
            # show all
            stocks = Stock.objects.filter(category=category).order_by('last_update')[0:10]

        return render_to_response('stock_list.html',
                                  context={'stock_list' : stocks,
                                           'category_list' : categories,
                                           'provider' : 'jd',
                                           'category' : int(category),
                                           })
    else:
        return render_to_response('base.html')
