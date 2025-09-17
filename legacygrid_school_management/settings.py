# settings.py
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps for security
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'two_factor',
    'axes',
    'django_extensions',
    'django_bootstrap5',
    'pwa',
    
    # Local apps
    'schools',
    'billing',  # Owner-only billing app
    'security',  # New security app for advanced features
    'premium',   # New premium features app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'axes.middleware.AxesMiddleware',  # Brute force protection
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # 2FA middleware
    'security.middleware.SecurityMiddleware',  # Custom security middleware
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
# IMPORTANT: Replace these with your actual Stripe keys in production
STRIPE_SECRET_KEY = 'sk_test_your_stripe_secret_key_here'  # Add your actual secret key
STRIPE_PUBLIC_KEY = 'pk_test_your_stripe_public_key_here'  # Add your actual public key  
STRIPE_PRICE_ID = 'price_your_stripe_price_id_here'  # Add your actual price ID
STRIPE_WEBHOOK_SECRET = 'whsec_your_webhook_secret_here'  # Add your webhook secret
DOMAIN = 'http://localhost:8000'  # Change to your domain in production

# === OPENAI API SETTINGS ===
OPENAI_API_KEY = 'sk-your-openai-api-key-here'  # Add your OpenAI API key

# === PAYMENT SETTINGS ===
PAYMENT_GATEWAYS = {
    'stripe': {
        'api_key': STRIPE_SECRET_KEY,
        'public_key': STRIPE_PUBLIC_KEY,
        'currency': 'USD',
        'mode': 'test',  # change to 'live' when ready
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
    },
    'premium': {
        'features': ['basic_dashboard', 'premium_dashboard', 'ai_reports', 'ai_chat', 'advanced_messaging'],
        'ai_access': True,
        'description': 'Premium plan with full access to all features including AI.',
    }
}
DEFAULT_TIER = 'free'
PREMIUM_TIER = 'premium'
AUTO_ACTIVATE_ON_PAYMENT = True  # instantly upgrades user tier on payment webhook

# === AI SETTINGS ===
AI_PROVIDER = 'openai'     # You pay for this one subscription only
AI_API_KEY = OPENAI_API_KEY  # Reference the secure key defined above

# === PAID FEATURE LOGIC ===
AI_FEATURES_REQUIRE_PAYMENT = True
PREMIUM_FEATURES_REQUIRE_PAYMENT = True

# === OWNER-ONLY BILLING ===
BILLING_OWNER_USERNAME = 'Uncle-T36'
ALLOW_ONLY_OWNER_BILLING = True

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

# === SECURITY ===
ALLOW_ONLY_OWNER_BILLING = True  # Only Uncle-T36 can see/manage billing

# === DOCS & SUPPORT ===
DOCUMENTATION_URL = 'https://github.com/Uncle-T36/legacygrid-school-management/blob/main/README.md'
SUPPORT_EMAIL = 'support@legacygrid.co.zw'

# === DEMO MODE ===
DEMO_MODE = True  # disables real payments until you switch to live mode

# === ADVANCED SECURITY SETTINGS ===

# Two-Factor Authentication
TWO_FACTOR_PATCH_ADMIN = True
TWO_FACTOR_CALL_GATEWAY = None
TWO_FACTOR_SMS_GATEWAY = None
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = 'two_factor:profile'
LOGOUT_REDIRECT_URL = 'two_factor:login'

# Axes (Brute Force Protection)
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_LOCKOUT_CALLABLE = 'axes.helpers.get_lockout_response'
AXES_LOCKOUT_TEMPLATE = 'security/lockout.html'
AXES_RESET_ON_SUCCESS = True

# Session Security
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Protection
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Password Validation (Enhanced)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
        'OPTIONS': {
            'last_passwords': 12  # Must not reuse last 12 passwords
        }
    },
    {
        'NAME': 'django_password_validators.password_character_requirements.password_validation.PasswordCharacterValidator',
        'OPTIONS': {
            'min_length_digit': 2,
            'min_length_alpha': 2,
            'min_length_special': 2,
            'min_length_lower': 2,
            'min_length_upper': 2,
            'special_characters': "~!@#$%^&*()_+{}\":;'[]"
        }
    },
]

# === AUTHENTICATION BACKENDS ===
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # AxesStandaloneBackend should be first
    'django.contrib.auth.backends.ModelBackend',
]

# === LICENSE & ANTI-CLONING SETTINGS ===
LICENSE_KEY = os.environ.get('LEGACYGRID_LICENSE_KEY', 'dev-license-key')
SCHOOL_ID_PREFIX = 'LG'
ANTI_CLONE_ENABLED = True
LICENSE_CHECK_INTERVAL = 86400  # 24 hours in seconds
ENVIRONMENT_FINGERPRINT_KEY = os.environ.get('ENV_FINGERPRINT_KEY', 'dev-fingerprint')

# === PREMIUM FEATURE GATING ===
FEATURE_GATES = {
    'advanced_analytics': 'premium',
    'custom_domains': 'premium', 
    'advanced_reporting': 'premium',
    'unlimited_users': 'premium',
    'priority_support': 'premium',
    'white_label': 'premium',
    'api_access': 'premium',
    'automated_backups': 'premium',
}

# === AUDIT LOGGING ===
AUDIT_LOG_ENABLED = True
AUDIT_LOG_RETENTION_DAYS = 365
SUSPICIOUS_ACTIVITY_THRESHOLD = 10

# === RATE LIMITING ===
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# === IP WHITELISTING ===
ADMIN_IP_WHITELIST = []  # Add IP addresses for admin access
GEO_BLOCKING_ENABLED = False  # Set to True in production
ALLOWED_COUNTRIES = ['ZW', 'ZA', 'US', 'GB']  # ISO country codes

# === BACKUP SETTINGS ===
BACKUP_ENABLED = True
BACKUP_ENCRYPTION_KEY = os.environ.get('BACKUP_ENCRYPTION_KEY', 'dev-backup-key')
BACKUP_SCHEDULE = '0 2 * * *'  # Daily at 2 AM
BACKUP_RETENTION_DAYS = 30

# === PWA SETTINGS ===
PWA_APP_NAME = 'LegacyGrid School Management'
PWA_APP_DESCRIPTION = 'Secure school management system'
PWA_APP_THEME_COLOR = '#000000'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': '/static/images/icons/icon-72x72.png',
        'sizes': '72x72'
    },
    {
        'src': '/static/images/icons/icon-96x96.png',
        'sizes': '96x96'
    },
    {
        'src': '/static/images/icons/icon-128x128.png',
        'sizes': '128x128'
    },
    {
        'src': '/static/images/icons/icon-144x144.png',
        'sizes': '144x144'
    },
    {
        'src': '/static/images/icons/icon-152x152.png',
        'sizes': '152x152'
    },
    {
        'src': '/static/images/icons/icon-192x192.png',
        'sizes': '192x192'
    },
    {
        'src': '/static/images/icons/icon-384x384.png',
        'sizes': '384x384'
    },
    {
        'src': '/static/images/icons/icon-512x512.png',
        'sizes': '512x512'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/images/icons/splash-640x1136.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]

# === CACHE SETTINGS ===
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# === LOGGING CONFIGURATION ===
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'legacygrid.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'security',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'axes': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
