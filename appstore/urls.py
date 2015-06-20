from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'appstore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^bijia/', include('bijia.urls')),
    url(r'^youku/', include('youku.urls')),
)
