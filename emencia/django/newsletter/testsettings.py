"""Settings for testing emencia.django.newsletter"""

SITE_ID = 1

ROOT_URLCONF = 'emencia.django.newsletter.urls'

DATABASES = {'default': {'NAME': 'newsletter_tests.db',
                         'ENGINE': 'django.db.backends.sqlite3'}}

INSTALLED_APPS = ['django.contrib.contenttypes',
                  'django.contrib.sites',
                  'tagging',
                  'emencia.django.newsletter']

ROOT_URLCONF = 'emencia.django.newsletter.urls'

LANGUAGE_CODE = 'fr'

LANGUAGES = (('fr', 'French'),
             ('en', 'English'),)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware']
