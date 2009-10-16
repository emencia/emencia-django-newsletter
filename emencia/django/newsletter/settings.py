"""Settings for emencia.django.newsletter"""
from django.conf import settings

INCLUDE_UNSUBSCRIPTION = getattr(settings, 'NEWSLETTER_INCLUDE_UNSUBSCRIPTION', True)

DEFAULT_HEADER_REPLY = getattr(settings. 'NEWSLETTER_DEFAULT_HEADER_REPLY', 'Emencia Newsletter<noreply@emencia.com>')
DEFAULT_HEADER_SENDER = getattr(settings. 'NEWSLETTER_DEFAULT_HEADER_SENDER', 'Emencia Newsletter<noreply@emencia.com>')

