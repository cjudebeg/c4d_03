from pathlib import Path
import os
import socket
import environ


env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',  
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django Debug Toolbar 
    'debug_toolbar',

    # Allauth apps for authentication
    'allauth',
    'allauth.account',

    # Our custom app 
    'authentication.apps.UsersConfig',
]

AUTH_USER_MODEL = 'authentication.CustomUser'


SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Configure INTERNAL_IPS for Docker:
# This snippet gets the container's IP addresses and converts them to allow the host.
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1"]

ROOT_URLCONF = 'a_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  
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

WSGI_APPLICATION = 'a_core.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',    
#         'NAME': 'c4d_db_it_3',                        
#         'USER': 'postgres',                           
#         'PASSWORD': 'postgres',
#         'HOST': 'db',  # Docker service name
#         'PORT': '5432',                               
#     }
# }


# Database configuration PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',    
        'NAME': os.environ.get('DATABASE_NAME'),                        
        'USER': os.environ.get('DATABASE_USER'),                          
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),  # Docker service name
        'PORT': os.environ.get('DATABASE_PORT'),                              
    }
}

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},

    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },

    {
        'NAME': 'authentication.validators.MaximumLengthValidator',
        'OPTIONS': {
            'max_length': 128,
        }
    },

    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},

    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},

    {'NAME': 'authentication.validators.NewPasswordNotSameAsOldValidator',    },  # New Password Not Same As Old Validator when it is reset

    {
        'NAME': 'authentication.validators.UnicodePasswordValidator',
    },

    {
        'NAME': 'authentication.validators.OneSpaceValidator',
    },
]

ACCOUNT_FORMS = {'signup': 'authentication.forms.CustomUserSignupForm'}

# Internationalisation settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Sydney'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Allauth configuration
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False 
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "profile"
ACCOUNT_LOGOUT_REDIRECT_URL = "account_login"

# Email backend for development (prints emails to console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Authentication backends used by Django Allauth
AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

