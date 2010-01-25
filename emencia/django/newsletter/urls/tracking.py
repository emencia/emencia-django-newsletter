"""Urls for the emencia.django.newsletter Tracking"""
from django.conf.urls.defaults import *

urlpatterns = patterns('emencia.django.newsletter.views.tracking',
                       url(r'^newsletter/(?P<slug>[-\w]+)/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           'view_newsletter_tracking',
                           name='newsletter_newsletter_tracking'),
                       url(r'^link/(?P<slug>[-\w]+)/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/(?P<link_id>\d+)/$',
                           'view_newsletter_tracking_link',
                           name='newsletter_newsletter_tracking_link'),
                       )

