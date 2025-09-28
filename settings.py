import os
import sys

# Note: This is now determined by whether python was invoked with -O (see ~/public_html/intepython.fcgi).
## OLD: DEBUG = True
DEBUG = __debug__
TEMPLATE_DEBUG = DEBUG

PROJECTPATH = os.path.dirname(__file__)
NLTKDATAPATH = os.path.join(PROJECTPATH, "nltk_data")
UPLOADFOLDER = os.path.join(PROJECTPATH, "static/questionimages")
UPLOADPREFIX = 'questionimages'
THUMBNAILFOLDER = os.path.join(PROJECTPATH, "static/thumbnails")
GENERATED_IMG = os.path.join(PROJECTPATH, "static/generated_img")
THUMBNAILPREFIX = 'thumbnails'
EXAM_TIMEOUT_PREFIX = '__assignment_time'

# New settings for term expansion
# See README.txt in algo directory for details
APPLY_SYNONYM_EXPANSION = True
## APPLY_ANCESTOR_EXPANSION = True
APPLY_ANCESTOR_EXPANSION = False
#
# Other algorithm-related settings
#
# Grammar checking
# NOTE: Disable because Bluehost doesn't support Java.
## OLD: APPLY_GRAMMAR_CHECKING = True
APPLY_GRAMMAR_CHECKING = False
#
# Summarization closeness
SUMMARIZE_CLOSENESS = True


LOGIN_URL = "/accounts/login/"

ADMINS = (
    # ('kenneth', 'kenneth@thingkingtop.com'),
    ('Swagat', 'swagat@egrovesystems.com'),
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
            'STORAGE_ENGINE': 'MyISAM', # used for south InnoDB would recommended 
            'ENGINE': 'django.db.backends.mysql',     # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'intemass',               # Or path to database file if using sqlite3.
            'USER': 'root',               # Not used with sqlite3.
            'PASSWORD': 'egrove',                # Not used with sqlite3.
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
LANGUAGE_CODE = 'zh_CN'
LANGUAGES_SUPPORTED = ('en', 'zh-cn',)
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Assignmentple: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = '/usr/local/lib/python2.6/dist-packages/Django-1.3.1-py2.6.egg/django/contrib/admin/media/'
# MEDIA_ROOT = os.path.join(PROJECTPATH, 'media')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Assignmentples: "http://media.lawrence.com/media/", "http://assignmentple.com/media/"
# MEDIA_URL = '/media/'

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

MEGAFORT_API_KEY="35e63a9420511478d7d2084d1f182430"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'intemass.common.middlewares.swfupload.SWFUploadMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'django_pdb.middleware.PdbMiddleware',
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
        },
    },
]

INTERNAL_IPS = ('127.0.0.1', '202.120.37.205',)
if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django_nose',
#    'django_pdb',
    'annoying',
    'common',
    'portal',
    'teacher',
    'student',
    'classroom',
    'itempool',
    'question',
    'paper',
    'assignment',
    'algo',
    'report',
    # 'debug_toolbar',
    'entity',
    'canvas',
    # 'south'  # Removed - Django 3.2 has built-in migrations
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Test runner (commented out for now)
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# NOSE_ARGS = ['--verbosity=2', '-s', '--nologcapture']

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

MASTER_USERS = ('Setter1',)

try:
    from .settings_local import *
except ImportError:
    pass
