import os

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/tmp/newsletter.db'
INSTALLED_APPS = ['django.contrib.contenttypes',
                  'tagging',
                  'emencia.django.newsletter',]
ROOT_URLCONF = 'emencia.django.newsletter.urls'

LANGUAGE_CODE = 'fr'

LANGUAGES = (
    ('fr', 'French'),
    ('en', 'English'),
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    )
