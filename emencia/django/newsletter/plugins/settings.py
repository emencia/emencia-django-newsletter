"""Settings for emencia.django.newsletter.plugins"""
from django.conf import settings

FORM_NAME = getattr(settings, 'SUBSCRIPTION_FORM_NAME', 'cms_subscription_form_plugin')
