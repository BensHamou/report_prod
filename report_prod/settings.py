from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

AUTHENTICATION_BACKENDS = [    
    'account.authentication.ApiBackend',
    'django.contrib.auth.backends.ModelBackend',
    ]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(BASE_DIR, 'secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

AUTH_USER_MODEL = 'account.User'

swappable = 'AUTH_USER_MODEL'

ADMIN_URL = 'puma_prod/admin/'

ALLOWED_HOSTS = ['*']

CSRF_COOKIE_SECURE = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "account",
    "report",
    'bootstrap5',
    'fontawesomefree',
    'django_filters',
    'widget_tweaks',
    'django_extensions',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "report_prod.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'account', 'templates', 'user'), os.path.join(BASE_DIR, 'account', 'templates', 'location'),
                 os.path.join(BASE_DIR, 'account', 'templates', 'horaire'), os.path.join(BASE_DIR, 'account', 'templates', 'fragment'), 
                 os.path.join(BASE_DIR, 'report', 'templates', 'report'), os.path.join(BASE_DIR, 'report', 'templates', 'product'), 
                 os.path.join(BASE_DIR, 'report', 'templates', 'numo_product'), os.path.join(BASE_DIR, 'report', 'templates', 'type_stop'), 
                 os.path.join(BASE_DIR, 'report', 'templates', 'reason_stop'), os.path.join(BASE_DIR, 'report', 'templates', 'modal')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "report_prod.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'prod_report',
        'USER': 'puma_u',
        'PASSWORD': 'puma_u',
        'HOST': '192.168.135.1',
        'PORT': '5432',
    }
}

        #'HOST': '192.168.56.1',

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / "static"]


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGIN_REDIRECT_URL = 'login_success'
LOGOUT_REDIRECT_URL = '/login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'pumaprod.reports@gmail.com'
EMAIL_HOST_PASSWORD = 'azefzqrsebojhusd'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'pumaprod.reports@gmail.com'
