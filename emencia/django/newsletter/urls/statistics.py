"""Urls for the emencia.django.newsletter statistics"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('emencia.django.newsletter.views.statistics',
                       url(r'^(?P<slug>[-\w]+)/$',
                           'view_newsletter_statistics',
                           name='newsletter_newsletter_statistics'),
                       url(r'^report/(?P<slug>[-\w]+)/$',
                           'view_newsletter_report',
                           name='newsletter_newsletter_report'),
                       url(r'^charts/(?P<slug>[-\w]+)/$',
                           'view_newsletter_charts',
                           name='newsletter_newsletter_charts'),
                       url(r'^density/(?P<slug>[-\w]+)/$',
                           'view_newsletter_density',
                           name='newsletter_newsletter_density'),
                       )
