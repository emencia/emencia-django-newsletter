"""Urls for the demo of emencia.django.newsletter"""
from django.contrib import admin
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import handler404
from django.conf.urls.defaults import handler500

admin.autodiscover()

urlpatterns = patterns('',
                       (r'^$', 'django.views.generic.simple.redirect_to',
                        {'url': '/admin/'}),
                       url(r'^newsletters/', include('emencia.django.newsletter.urls')),
                       url(r'^i18n/', include('django.conf.urls.i18n')),
                       url(r'^admin/', include(admin.site.urls)),
                       )
