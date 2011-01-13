"""Context Processors for emencia.django.newsletter"""
from emencia.django.newsletter.settings import MEDIA_URL


def media(request):
    """Adds media-related context variables to the context"""
    return {'NEWSLETTER_MEDIA_URL': MEDIA_URL}
