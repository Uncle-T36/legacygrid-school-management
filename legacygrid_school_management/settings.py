import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes', 'on')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'schools',
    'billing',  # New billing app for payment management
    'account',  # Account app for user profile management
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

# Login URLs
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'

# === STRIPE PAYMENT SETTINGS ===
# Load from environment variables for production security
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_stripe_secret_key_here')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'pk_test_your_stripe_public_key_here')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID', 'price_your_stripe_price_id_here')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret_here')
DOMAIN = os.getenv('DOMAIN', 'http://localhost:8000')

# === OPENAI API SETTINGS ===
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-your-openai-api-key-here')

# === PAYMENT SETTINGS ===
PAYMENT_GATEWAYS = {
    'stripe': {
        'api_key': STRIPE_SECRET_KEY,
        'public_key': STRIPE_PUBLIC_KEY,
        'currency': 'USD',
        'mode': 'test',  # change to 'live' when ready
    },
    'paypal': {
        'client_id': os.getenv('PAYPAL_CLIENT_ID', 'test-client-id'),
        'client_secret': os.getenv('PAYPAL_CLIENT_SECRET', 'test-client-secret'),
        'mode': os.getenv('PAYPAL_MODE', 'sandbox'),  # change to 'live'
    },
    # Zimbabwe Mobile Money
    'ecocash': {
        'merchant_code': os.getenv('ECOCASH_MERCHANT_CODE', 'test-merchant'),
        'api_url': os.getenv('ECOCASH_API_URL', 'https://api.sandbox.ecocash.co.zw/'),
        'mode': os.getenv('ECOCASH_MODE', 'test'),
    },
    'onemoney': {
        'merchant_code': os.getenv('ONEMONEY_MERCHANT_CODE', 'test-merchant'),
        'api_url': os.getenv('ONEMONEY_API_URL', 'https://sandbox.onemoney.co.zw/api/'),
        'mode': os.getenv('ONEMONEY_MODE', 'test'),
    },
    # Add more as needed
}


# === CURRENCY CONVERSION ===
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'USD')
SUPPORTED_CURRENCIES = os.getenv('SUPPORTED_CURRENCIES', 'USD,ZWL,ZAR,NGN,GBP,EUR').split(',')
CURRENCY_CONVERSION_API_URL = 'https://api.exchangeratesapi.io/latest'  # Free for dev, use premium for live

# === SUBSCRIPTION TIERS ===
SUBSCRIPTION_TIERS = {
    'free': {
        'features': ['basic_dashboard', 'basic_messaging'],
        'ai_access': False,
        'description': 'Free plan with limited features, no AI access.',
    },
    'premium': {
        'features': ['basic_dashboard', 'premium_dashboard', 'ai_reports', 'ai_chat', 'advanced_messaging'],
        'ai_access': True,
        'description': 'Premium plan with full access to all features including AI.',
    }
}
DEFAULT_TIER = os.getenv('DEFAULT_TIER', 'free')
PREMIUM_TIER = os.getenv('PREMIUM_TIER', 'premium')
AUTO_ACTIVATE_ON_PAYMENT = os.getenv('AUTO_ACTIVATE_ON_PAYMENT', 'True').lower() in ('true', '1', 'yes', 'on')

# === AI SETTINGS ===
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')     # You pay for this one subscription only
AI_API_KEY = OPENAI_API_KEY  # Reference the secure key defined above

# === PAID FEATURE LOGIC ===
AI_FEATURES_REQUIRE_PAYMENT = os.getenv('AI_FEATURES_REQUIRE_PAYMENT', 'True').lower() in ('true', '1', 'yes', 'on')
PREMIUM_FEATURES_REQUIRE_PAYMENT = os.getenv('PREMIUM_FEATURES_REQUIRE_PAYMENT', 'True').lower() in ('true', '1', 'yes', 'on')

# === OWNER-ONLY BILLING ===
BILLING_OWNER_USERNAME = os.getenv('OWNER_USERNAME', 'Uncle-T36')
ALLOW_ONLY_OWNER_BILLING = os.getenv('ALLOW_ONLY_OWNER_BILLING', 'True').lower() in ('true', '1', 'yes', 'on')

# === MESSAGING SETTINGS ===
DEFAULT_LANGUAGES = os.getenv('DEFAULT_LANGUAGES', 'en,sn,nd').split(',')  # English, Shona, Ndebele
LANGUAGE_TEMPLATES = {
    'en': 'templates/messages_en.txt',
    'sn': 'templates/messages_sn.txt',
    'nd': 'templates/messages_nd.txt',
}
SEND_SMS = os.getenv('SEND_SMS', 'True').lower() in ('true', '1', 'yes', 'on')
SEND_EMAIL = os.getenv('SEND_EMAIL', 'True').lower() in ('true', '1', 'yes', 'on')

# === PARENT PROFILE ===
PARENT_LANGUAGE_FIELD = 'preferred_language'

# === SECURITY ===
# Duplicate line - remove this one
# ALLOW_ONLY_OWNER_BILLING = True  # Only Uncle-T36 can see/manage billing

# === DOCS & SUPPORT ===
DOCUMENTATION_URL = os.getenv('DOCUMENTATION_URL', 'https://github.com/Uncle-T36/legacygrid-school-management/blob/main/README.md')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@legacygrid.co.zw')

# === DEMO MODE ===
DEMO_MODE = os.getenv('DEMO_MODE', 'True').lower() in ('true', '1', 'yes', 'on')  # disables real payments until you switch to live mode
