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

    'django.middleware.locale.LocaleMiddleware',      # ← add this
]

# Configure INTERNAL_IPS for Docker 
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1"]

ROOT_URLCONF = 'a_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'c4d' / 'templates',   # ‑‑ add this line, keep it first
            BASE_DIR / 'templates',           # existing global folder
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

WSGI_APPLICATION = 'a_core.wsgi.application'

# Database configuration PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
        'user_attributes': ('email', 'username'),
        'max_similarity': 0.7,
        }
    },

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

    {'NAME': 'authentication.validators.NewPasswordNotSameAsOldValidator',},  # New Password Not Same As Old Validator

    {
        'NAME': 'authentication.validators.UnicodePasswordValidator',
    },

]

ACCOUNT_FORMS = {
    'signup': 'authentication.forms.CustomUserSignupForm',
    'add_email': 'authentication.forms.AddEmailForm',
}

# Internationalisation settings
LANGUAGE_CODE = 'en-gb'
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
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_CHANGE_EMAIL = True

# ACCOUNT_SIGNUP_FORM_CLASS = "authentication.forms.CustomUserSignupForm"


ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = False

# Form errors will be presented as messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Email backend for development 
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@example.com"

# Authentication backends used by Django Allauth
AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]
