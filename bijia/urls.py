from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'appstore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^index', 'bijia.views.stocklistview'),
    url(r'^addip', 'bijia.views.addipview'),
    url(r'^ip',    'bijia.views.serverview'),
)
