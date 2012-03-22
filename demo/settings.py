"""Settings for the demo of emencia.django.newsletter"""
import os

gettext = lambda s: s

DEBUG = True

DATABASES = {'default':
             {'ENGINE': 'django.db.backends.sqlite3',
              'NAME': os.path.join(os.path.dirname(__file__), 'demo.db')}
             }

STATIC_URL = '/static/'

MEDIA_URL = 'http://localhost:8000/'

SECRET_KEY = 'jkjf7878fsdok-|767sjdvjsm_qcskhvs$:?shf67dd66%&sfj'

USE_I18N = True
USE_L10N = True

SITE_ID = 1

LANGUAGE_CODE = 'en'

LANGUAGES = (('en', gettext('English')),
             ('fr', gettext('French')),
             ('de', gettext('German')),
             ('es', gettext('Spanish')),
             ('es_DO', gettext('Spanish (Dominican Republic)')),
             ('it', gettext('Italian')),
             ('pt', gettext('Portuguese')),
             ('pt_BR', gettext('Portuguese (Brazilian)')),
             ('nl', gettext('Dutch')),
             ('cs', gettext('Czech')),
             ('fo', gettext('Faroese')),
             ('ja', gettext('Japanese')),
             ('sk_SK', gettext('Slovak (Slovakia)')),
             ('sl', gettext('Slovenian')),
             ('zh_CN', gettext('Chinese (China)')),)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )

ROOT_URLCONF = 'demo.urls'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'tagging',
    'emencia.django.newsletter',
    )

# --- templates --- start -----------------------------------------------------
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)
# --- templates --- end -------------------------------------------------------
