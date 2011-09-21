"""Settings for testing emencia.django.newsletter"""

SITE_ID = 1

USE_I18N = False

ROOT_URLCONF = 'emencia.django.newsletter.urls'

DATABASES = {'default': {'NAME': 'newsletter_tests.db',
                         'ENGINE': 'django.db.backends.sqlite3'}}

INSTALLED_APPS = ['django.contrib.contenttypes',
                  'django.contrib.sites',
                  'django.contrib.auth',
                  'tagging',
                  'emencia.django.newsletter']
