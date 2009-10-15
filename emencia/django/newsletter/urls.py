"""Urls for the newsletter"""
from django.conf.urls.defaults import *

from emencia.django.newsletter.models import Newsletter

newsletter_conf = {'queryset': Newsletter.objects.all()}


urlpatterns = patterns('django.views.generic.list_detail',
                       url(r'^(?P<slug>[-\w]+)/$', 'object_detail',
                           newsletter_conf, 'newsletter_newsletter_detail'),
                       )

