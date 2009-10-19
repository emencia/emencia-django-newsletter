"""Urls for the emencia.django.newsletter"""
from django.conf.urls.defaults import *

from emencia.django.newsletter.models import Newsletter

urlpatterns = patterns('emencia.django.newsletter.views',
                       url(r'^preview/(?P<slug>[-\w]+)/$',
                           'view_newsletter_preview',
                           name='newsletter_newsletter_preview'),
                       url(r'^tracking/(?P<slug>[-\w]+)/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           'view_newsletter_tracking',
                           name='newsletter_newsletter_tracking'),
                       url(r'^unsubscribe/(?P<slug>[-\w]+)/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           'view_mailinglist_unsubscribe',
                           name='newsletter_mailinglist_unsubscribe'),
                       url(r'^(?P<slug>[-\w]+)/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           'view_newsletter_contact',
                           name='newsletter_newsletter_contact'),                       
                       )

