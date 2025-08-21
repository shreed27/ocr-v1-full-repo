import os,sys
PROJECTPATH = os.path.dirname(__file__)
DEBUG = False 
if 'test' in sys.argv:
    DATABASES = {
         'default':{
             'ENGINE': 'django.db.backends.sqlite3'
         }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',     # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'intepyth_db',               # Or path to database file if using sqlite3.
            'USER': 'intepyth_db',               # Not used with sqlite3.
            'PASSWORD': '88EEEzKsZC(K',                # Not used with sqlite3.
            'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                               # Set to empty string for default. Not used with sqlite3
        }
    }


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'intemass.common.middlewares.swfupload.SWFUploadMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_nose',
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
    #'debug_toolbar',
    'intemass.entity',
    'intemass.canvas',
)

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECTPATH, "images"),
)

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
        'console':{
            'level': 'INFO',
            'class':'logging.StreamHandler',
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
            'handlers': ['console'],
            'level': 'INFO',
        },
        'intemass': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    }
}



