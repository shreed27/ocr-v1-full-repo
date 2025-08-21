import os
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECTPATH = os.path.dirname(__file__)
NLTKDATAPATH = os.path.join(PROJECTPATH, "nltk_data")
UPLOADFOLDER = os.path.join(PROJECTPATH, "images/questionimages")
UPLOADPREFIX = 'questionimages'
THUMBNAILFOLDER = os.path.join(PROJECTPATH, "images/thumbnails")
GENERATED_IMG = os.path.join(PROJECTPATH, "images/generated_img")
THUMBNAILPREFIX = 'thumbnails'
EXAM_TIMEOUT_PREFIX = '__assignment_time'

# New settings for term expansion
# See README.txt in algo directory for details
APPLY_SYNONYM_EXPANSION = True
APPLY_ANCESTOR_EXPANSION = True

LOGIN_URL = "/accounts/login/"

ADMINS = (
    ('kenneth', 'kenneth@thingkingtop.com'),
)
MANAGERS = ADMINS

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3'
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',     # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'intemass',               # Or path to database file if using sqlite3.
            'USER': 'root',               # Not used with sqlite3.
            'PASSWORD': '1',                # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                               # Set to empty string for default. Not used with sqlite3
        }
    }


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Singapore'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Assignmentple: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = '/usr/local/lib/python2.6/dist-packages/Django-1.3.1-py2.6.egg/django/contrib/admin/media/'
MEDIA_ROOT = os.path.join(PROJECTPATH, 'media')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Assignmentples: "http://media.lawrence.com/media/", "http://assignmentple.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Assignmentple: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECTPATH, 'static')

# URL prefix for static files.
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Assignmentples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECTPATH, "images"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r(c4gh06w(*ud6k1bb_*fum@l$c-+)#9ghq@$f=3gbo4hghft*'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'intemass.common.middlewares.swfupload.SWFUploadMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'django_pdb.middleware.PdbMiddleware',
)

ROOT_URLCONF = "intemass.urls"

TEMPLATE_DIRS = ()
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    #'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

INTERNAL_IPS = ('127.0.0.1', '202.120.37.205',)
if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_nose',
#    'django_pdb',
    'intemass.annoying',
    'intemass.common',
    'intemass.portal',
    'intemass.teacher',
    'intemass.student',
    'intemass.classroom',
    'intemass.itempool',
    'intemass.question',
    'intemass.paper',
    'intemass.assignment',
    'intemass.algo',
    'intemass.report',
    'debug_toolbar',
    'intemass.entity',
    'intemass.canvas',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--verbosity=2', '-s', '--nologcapture']

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s][%(name)s#%(funcName)s (%(lineno)d)] - %(levelname)s : %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'consoles': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'consolev': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'intemass': {
            'handlers': ['consolev'],
            'level': 'DEBUG',
        },
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.163.com'
EMAIL_HOST_USER = 'twoeigmp@163.com'
EMAIL_HOST_PASSWORD = '28mptest'
EMAIL_PORT = 25

try:
    from settings_local import *
except ImportError:
    pass
