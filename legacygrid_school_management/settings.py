# settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'schools',
    # add any new payment/messaging apps here
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'legacygrid_school_management.urls'

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

WSGI_APPLICATION = 'legacygrid_school_management.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === STRIPE PAYMENT SETTINGS ===
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_51HxxxYourTestKeyHere')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51HxxxYourTestKeyHere')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_test_webhook_secret')
STRIPE_LIVE_MODE = os.getenv('STRIPE_LIVE_MODE', 'False').lower() == 'true'

# Stripe Product and Price Configuration
STRIPE_PREMIUM_PRICE_ID = os.getenv('STRIPE_PREMIUM_PRICE_ID', 'price_test_premium_monthly')
STRIPE_PREMIUM_PRODUCT_ID = os.getenv('STRIPE_PREMIUM_PRODUCT_ID', 'prod_test_premium')

# === PAYMENT SETTINGS ===
PAYMENT_GATEWAYS = {
    'stripe': {
        'api_key': STRIPE_SECRET_KEY,
        'public_key': STRIPE_PUBLISHABLE_KEY,
        'webhook_secret': STRIPE_WEBHOOK_SECRET,
        'currency': 'USD',
        'mode': 'live' if STRIPE_LIVE_MODE else 'test',
        'premium_price_id': STRIPE_PREMIUM_PRICE_ID,
        'premium_product_id': STRIPE_PREMIUM_PRODUCT_ID,
    },
    'paypal': {
        'client_id': 'test-client-id',
        'client_secret': 'test-client-secret',
        'mode': 'sandbox',  # change to 'live'
    },
    # Zimbabwe Mobile Money Placeholders
    'ecocash': {
        'merchant_code': 'test-merchant',
        'api_url': 'https://api.sandbox.ecocash.co.zw/',
        'mode': 'test',
    },
    'onemoney': {
        'merchant_code': 'test-merchant',
        'api_url': 'https://sandbox.onemoney.co.zw/api/',
        'mode': 'test',
    },
    # Add more as needed
}

# === CURRENCY CONVERSION ===
DEFAULT_CURRENCY = 'USD'
SUPPORTED_CURRENCIES = ['USD', 'ZWL', 'ZAR', 'NGN', 'GBP', 'EUR']
CURRENCY_CONVERSION_API_URL = 'https://api.exchangeratesapi.io/latest'  # Free for dev, use premium for live

# === SUBSCRIPTION TIERS ===
SUBSCRIPTION_TIERS = {
    'free': {
        'features': ['basic_dashboard', 'basic_messaging'],
        'ai_access': False,
        'description': 'Free plan with limited features, no AI access.',
        'price': 0,
        'stripe_price_id': None,
    },
    'premium': {
        'features': ['basic_dashboard', 'premium_dashboard', 'ai_reports', 'ai_chat', 'advanced_messaging'],
        'ai_access': True,
        'description': 'Premium plan with full access to all features including AI.',
        'price': 29.99,
        'stripe_price_id': STRIPE_PREMIUM_PRICE_ID,
    }
}
DEFAULT_TIER = 'free'
PREMIUM_TIER = 'premium'
AUTO_ACTIVATE_ON_PAYMENT = True  # instantly upgrades user tier on payment webhook

# === AI SETTINGS ===
AI_PROVIDER = 'openai'     # You pay for this one subscription only
AI_API_KEY = 'sk_test_ai_key'  # Add your live key here when ready

# === PAID FEATURE LOGIC ===
AI_FEATURES_REQUIRE_PAYMENT = True
PREMIUM_FEATURES_REQUIRE_PAYMENT = True

# === OWNER-ONLY BILLING & SECURITY ===
BILLING_OWNER_USERNAME = 'Uncle-T36'
ALLOW_ONLY_OWNER_BILLING = True

# Billing Access Control Settings
BILLING_ACCESS_DENIED_MESSAGE = (
    "Access denied. Billing and subscription management is restricted to the system owner only. "
    "Contact the administrator for assistance with billing matters."
)

SUBSCRIPTION_ACCESS_DENIED_MESSAGE = (
    "Subscription management is restricted to authorized personnel only. "
    "Please contact support@legacygrid.co.zw for subscription assistance."
)

# Security settings for billing
REQUIRE_BILLING_OWNER_CONFIRMATION = True
BILLING_SESSION_TIMEOUT = 300  # 5 minutes for billing sessions
LOG_BILLING_ACCESS_ATTEMPTS = True

# === MESSAGING SETTINGS ===
DEFAULT_LANGUAGES = ['en', 'sn', 'nd']  # English, Shona, Ndebele
LANGUAGE_TEMPLATES = {
    'en': 'templates/messages_en.txt',
    'sn': 'templates/messages_sn.txt',
    'nd': 'templates/messages_nd.txt',
}
SEND_SMS = True
SEND_EMAIL = True

# === PARENT PROFILE ===
PARENT_LANGUAGE_FIELD = 'preferred_language'

# === DOCS & SUPPORT ===
DOCUMENTATION_URL = 'https://github.com/Uncle-T36/legacygrid-school-management/blob/main/README.md'
SUPPORT_EMAIL = 'support@legacygrid.co.zw'

# === DEMO MODE ===
DEMO_MODE = True  # disables real payments until you switch to live mode

# === LOGGING CONFIGURATION ===
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'billing_access.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'billing': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
