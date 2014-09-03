import os


here = lambda x: os.path.join(os.path.dirname(os.path.abspath(__file__)), x)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = 'k&s@!df&@nsm+02ib*z6k)c^$85crmng3bil@-+v7c4%89xhcq'  # Not used anywhere really
INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'mongoengine.django.mongo_auth',
	'api',
	'web',
)
MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.core.context_processors.tz',
	'django.contrib.messages.context_processors.messages',
)
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.dummy'
	}
}
ROOT_URLCONF = 'db.urls'
WSGI_APPLICATION = 'db.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'
STATIC_ROOT = ''
STATIC_URL = '/media/admin/'
APPEND_SLASH = False


try:
	from .localsettings import *
except:
	print('There seems to be an error in your localsettings.py file. Maybe you haven\'t copied it yet from the example.')