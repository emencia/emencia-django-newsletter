"""Urls for the emencia.django.newsletter Mailing List"""
from django.conf.urls.defaults import *

urlpatterns = patterns('emencia.django.newsletter.views.mailing_list',
                       url(r'^unsubscribe/(?P<slug>[-\w]+)/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           'view_mailinglist_unsubscribe',
                           name='newsletter_mailinglist_unsubscribe'),
                       )
