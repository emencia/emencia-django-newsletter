"""Default urls for the emencia.django.newsletter"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',                       
                       (r'^mailing/', include('emencia.django.newsletter.urls.mailing_list')),
                       (r'^tracking/', include('emencia.django.newsletter.urls.tracking')),
                       (r'^statistics/', include('emencia.django.newsletter.urls.statistics')),
                       (r'^', include('emencia.django.newsletter.urls.newsletter')),
                       )
