"""Default urls for the emencia.django.newsletter"""

# --- subscriber verification --- start ---------------------------------------
from emencia.django.newsletter.settings import SUBSCRIBER_VERIFICATION
# --- subscriber verification --- end -----------------------------------------
from django.conf.urls.defaults import url, include, patterns

urlpatterns = patterns('',
    url(r'^mailing/', include('emencia.django.newsletter.urls.mailing_list')),
    url(r'^tracking/', include('emencia.django.newsletter.urls.tracking')),
    url(r'^statistics/', include('emencia.django.newsletter.urls.statistics')),
)

# --- subscriber verification --- start ---------------------------------------
if SUBSCRIBER_VERIFICATION:
    urlpatterns += patterns('',
        url(r'^subscribe/',
            include('emencia.django.newsletter.urls.verification')
        ),
    )
# --- subscriber verification --- end -----------------------------------------

urlpatterns += patterns('',
    url(r'^', include('emencia.django.newsletter.urls.newsletter')),
)
