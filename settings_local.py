import os,sys
PROJECTPATH = os.path.dirname(__file__)

# Note: DEBUG now determined by absence of python -O switch
## OLD: DEBUG = False
DEBUG = __debug__

ADMINS = (
    ('Vaim', 'dev@v-aim.com'),
    #('Swagat', 'swagat@egrovesystems.com'),
    # ('sengottuvel', 'sengottuvel@egrovesystems.com'),
)

if 'test' in sys.argv:
    DATABASES = {
         'default':{
             'ENGINE': 'django.db.backends.sqlite3',
             'NAME': ':memory:',
         }
    }
else:
    # Use SQLite for development testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECTPATH, 'intemass_dev.db'),
        }
    }
    
    # MySQL configuration (commented out for now)
    # DATABASES = {
    #     'default': {
    #         'STORAGE_ENGINE': 'MyISAM', # used for south InnoDB would recommended
    #         'ENGINE': 'django.db.backends.mysql',     # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    #         # 'NAME': 'intemass_live',               # Or path to database file if using sqlite3.
    #         'NAME': 'intemass_live_merge',               # Or path to database file if using sqlite3.
    #         'USER': 'intemass_dbuser',               # Not used with sqlite3.
    #         'PASSWORD': 'Intemass@234',                # Not used with sqlite3.
    #         'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
    #         'PORT': '',                               # Set to empty string for default. Not used with sqlite3
    #     }
    # }


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
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_nose',
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
    'mcq',
    'cpm',
    'entity',
    'canvas',
    # South removed - Django 3.2 has built-in migrations
]

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECTPATH, "images"),
    #os.path.join(PROJECTPATH, "static"),
    # os.path.join(PROJECTPATH, "static/images"),
)

# OCR API Configuration
OCR_API_SETTINGS = {
    'API_URL': 'http://localhost:8080/api/process',
    'API_KEY': '',  # No API key needed for local development
    'TIMEOUT': 30,  # API timeout in seconds
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB max file size
    'ALLOWED_FORMATS': ['jpg', 'jpeg', 'png', 'pdf', 'tiff'],
    'TEMP_UPLOAD_DIR': os.path.join(PROJECTPATH, 'temp_ocr_uploads'),
}


# Django 3.2 required settings
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Templates configuration for Django 3.2
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECTPATH, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECTPATH, 'staticfiles')

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECTPATH, 'media')

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
        },
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

# Note: by default intepython is run with -O switch (see ~/public_html/intepython.fcgi).
# The console not used to avoid overwhelming bluehost apache logs.
# Based on http://stackoverflow.com/questions/5739830/simple-log-to-file-example-for-django-1-3
if DEBUG:
    LOGGING['handlers']['logfile'] = {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': PROJECTPATH + "/django.log",
            'maxBytes': 10485760,
            'backupCount': 2,
            'formatter': 'verbose',
        };
    LOGGING['loggers']['intemass'] = {
        'handlers': ['logfile'],
        'level': 'DEBUG',
        'handlers': ['logfile'],
        'level': 'DEBUG',
        };
        
