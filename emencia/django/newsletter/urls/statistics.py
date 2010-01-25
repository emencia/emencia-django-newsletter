"""Urls for the emencia.django.newsletter statistics"""
from django.conf.urls.defaults import *

urlpatterns = patterns('emencia.django.newsletter.views.statistics',
                       url(r'^(?P<slug>[-\w]+)/$',
                           'view_newsletter_statistics',
                           name='newsletter_newsletter_statistics'),
                       url(r'^charts/(?P<slug>[-\w]+)/$',
                           'view_newsletter_charts',
                           name='newsletter_newsletter_charts'),
                       )

