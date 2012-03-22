"""Settings for emencia.django.newsletter"""
import string
from django.conf import settings

BASE64_IMAGES = {
    'gif': 'AJEAAAAAAP///////wAAACH5BAEHAAIALAAAAAABAAEAAAICVAEAOw==',
    'png': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAABBJREFUeNpi+P//PwNAgAEACPwC/tuiTRYAAAAASUVORK5CYII=',
    'jpg': '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBAQFBAYFBQYJBgUGCQsIBgYICwwKCgsKCgwQDAwMDAwMEAwODxAPDgwTExQUExMcGxsbHCAgICAgICAgICD/2wBDAQcHBw0MDRgQEBgaFREVGiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICD/wAARCAABAAEDAREAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACP/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AVIP/2Q=='
    }

USE_WORKGROUPS = getattr(settings, 'NEWSLETTER_USE_WORKGROUPS', False)
USE_UTM_TAGS = getattr(settings, 'NEWSLETTER_USE_UTM_TAGS', True)
USE_TINYMCE = getattr(settings, 'NEWSLETTER_USE_TINYMCE',
                      'tinymce' in settings.INSTALLED_APPS)

USE_PRETTIFY = getattr(settings, 'NEWSLETTER_USE_PRETTIFY', True)

MAILER_HARD_LIMIT = getattr(settings, 'NEWSLETTER_MAILER_HARD_LIMIT', 10000)

INCLUDE_UNSUBSCRIPTION = getattr(settings, 'NEWSLETTER_INCLUDE_UNSUBSCRIPTION', True)

UNIQUE_KEY_LENGTH = getattr(settings, 'NEWSLETTER_UNIQUE_KEY_LENGTH', 8)
UNIQUE_KEY_CHAR_SET = getattr(settings, 'NEWSLETTER_UNIQUE_KEY_CHAR_SET', string.ascii_uppercase + string.digits)

DEFAULT_HEADER_SENDER = getattr(settings, 'NEWSLETTER_DEFAULT_HEADER_SENDER',
                                'Emencia Newsletter<noreply@emencia.com>')
DEFAULT_HEADER_REPLY = getattr(settings, 'NEWSLETTER_DEFAULT_HEADER_REPLY',
                               DEFAULT_HEADER_SENDER)

TRACKING_LINKS = getattr(settings, 'NEWSLETTER_TRACKING_LINKS', True)

TRACKING_IMAGE_FORMAT = getattr(settings, 'NEWSLETTER_TRACKING_IMAGE_FORMAT', 'jpg')
TRACKING_IMAGE = getattr(settings, 'NEWSLETTER_TRACKING_IMAGE',
                         BASE64_IMAGES[TRACKING_IMAGE_FORMAT])

SLEEP_BETWEEN_SENDING = getattr(
    settings, 'NEWSLETTER_SLEEP_BETWEEN_SENDING', 0)
RESTART_CONNECTION_BETWEEN_SENDING = getattr(
    settings, 'NEWSLETTER_RESTART_CONNECTION_BETWEEN_SENDING', False)

BASE_PATH = getattr(settings, 'NEWSLETTER_BASE_PATH', 'uploads/newsletter')

# --- tracking ignore anchor --- start ----------------------------------------
TRACKING_IGNORE_ANCHOR = getattr(
    settings,
    'NEWSLETTER_TRACKING_IGNORE_ANCHOR',
    False
)
# --- tracking ignore anchor --- end ------------------------------------------

# --- subscriber verification --- start ---------------------------------------
SUBSCRIBER_VERIFICATION = getattr(
    settings,
    'NEWSLETTER_SUBSCRIBER_VERIFICATION',
    True
)
# --- subscriber verification --- end -----------------------------------------

# --- templates --- start -----------------------------------------------------
USE_TEMPLATE = getattr( settings, 'NEWSLETTER_USE_TEMPLATE', True)
# --- templates --- end -------------------------------------------------------
