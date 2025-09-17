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
    'core',  # Core multi-tenant and internationalization support
    'schools',
    'billing',  # New billing app for payment management
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Enable i18n
    'core.middleware.TenantMiddleware',  # Multi-tenant support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AuditLogMiddleware',  # Audit logging
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
USE_L10N = True
USE_TZ = True

# === INTERNATIONALIZATION SETTINGS ===
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
    ('pt', 'Português'),
    ('ar', 'العربية'),
    ('sw', 'Kiswahili'),
    ('es', 'Español'),
    ('zh', '中文'),
    ('hi', 'हिन्दी'),
    ('ur', 'اردو'),
    ('am', 'አማርኛ'),
    ('yo', 'Yorùbá'),
    ('ig', 'Igbo'),
    ('ha', 'Hausa'),
    ('zu', 'isiZulu'),
    ('af', 'Afrikaans'),
    ('sn', 'chiShona'),
    ('nd', 'isiNdebele'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# RTL Languages
RTL_LANGUAGES = ['ar', 'ur', 'he', 'fa']

# === CURRENCY AND REGIONAL SETTINGS ===
DEFAULT_CURRENCY = 'USD'
SUPPORTED_CURRENCIES = [
    'USD', 'EUR', 'GBP', 'ZAR', 'NGN', 'KES', 'UGX', 'TZS', 'GHS', 
    'ZWL', 'BWP', 'MWK', 'ZMW', 'INR', 'PKR', 'BDT', 'LKR', 'CNY',
    'JPY', 'KRW', 'THB', 'VND', 'IDR', 'MYR', 'SGD', 'PHP', 'AUD',
    'CAD', 'BRL', 'ARS', 'CLP', 'PEN', 'COP', 'MXN', 'EGP', 'MAD',
    'DZD', 'TND', 'ETB', 'RWF', 'XAF', 'XOF'
]

# Currency conversion API
CURRENCY_CONVERSION_API_URL = 'https://api.exchangeratesapi.io/latest'
CURRENCY_CONVERSION_API_KEY = ''  # Add your API key

# === COUNTRY-SPECIFIC SETTINGS ===
DEFAULT_COUNTRIES = [
    {'code': 'USA', 'name': 'United States', 'currency': 'USD', 'locale': 'en-US'},
    {'code': 'ZWE', 'name': 'Zimbabwe', 'currency': 'USD', 'locale': 'en-ZW'},
    {'code': 'ZAF', 'name': 'South Africa', 'currency': 'ZAR', 'locale': 'en-ZA'},
    {'code': 'NGA', 'name': 'Nigeria', 'currency': 'NGN', 'locale': 'en-NG'},
    {'code': 'KEN', 'name': 'Kenya', 'currency': 'KES', 'locale': 'en-KE'},
    {'code': 'UGA', 'name': 'Uganda', 'currency': 'UGX', 'locale': 'en-UG'},
    {'code': 'TZA', 'name': 'Tanzania', 'currency': 'TZS', 'locale': 'sw-TZ'},
    {'code': 'GHA', 'name': 'Ghana', 'currency': 'GHS', 'locale': 'en-GH'},
    {'code': 'BWA', 'name': 'Botswana', 'currency': 'BWP', 'locale': 'en-BW'},
    {'code': 'IND', 'name': 'India', 'currency': 'INR', 'locale': 'en-IN'},
    {'code': 'FRA', 'name': 'France', 'currency': 'EUR', 'locale': 'fr-FR'},
    {'code': 'DEU', 'name': 'Germany', 'currency': 'EUR', 'locale': 'de-DE'},
    {'code': 'GBR', 'name': 'United Kingdom', 'currency': 'GBP', 'locale': 'en-GB'},
    {'code': 'BRA', 'name': 'Brazil', 'currency': 'BRL', 'locale': 'pt-BR'},
    {'code': 'ARE', 'name': 'United Arab Emirates', 'currency': 'AED', 'locale': 'ar-AE'},
    {'code': 'SAU', 'name': 'Saudi Arabia', 'currency': 'SAR', 'locale': 'ar-SA'},
    {'code': 'EGY', 'name': 'Egypt', 'currency': 'EGP', 'locale': 'ar-EG'},
    {'code': 'MAR', 'name': 'Morocco', 'currency': 'MAD', 'locale': 'ar-MA'},
]

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

# === PAYMENT GATEWAY CONFIGURATIONS ===
PAYMENT_GATEWAYS = {
    'stripe': {
        'api_key': STRIPE_SECRET_KEY,
        'public_key': STRIPE_PUBLIC_KEY,
        'currency': 'USD',
        'mode': 'test',  # change to 'live' when ready
        'countries': ['USA', 'GBR', 'CAN', 'AUS', 'DEU', 'FRA', 'ITA', 'ESP', 'NLD', 'BEL'],
        'webhook_secret': STRIPE_WEBHOOK_SECRET,
    },
    'paystack': {
        'public_key': 'pk_test_your_paystack_public_key_here',
        'secret_key': 'sk_test_your_paystack_secret_key_here',
        'currency': 'NGN',
        'mode': 'test',
        'countries': ['NGA', 'GHA', 'ZAF', 'KEN'],
        'api_url': 'https://api.paystack.co',
    },
    'flutterwave': {
        'public_key': 'FLWPUBK_TEST-your_flutterwave_public_key_here',
        'secret_key': 'FLWSECK_TEST-your_flutterwave_secret_key_here',
        'currency': 'NGN',
        'mode': 'test',
        'countries': ['NGA', 'GHA', 'KEN', 'UGA', 'TZA', 'RWA', 'ZMB'],
        'api_url': 'https://api.flutterwave.com/v3',
    },
    'paypal': {
        'client_id': 'test-client-id',
        'client_secret': 'test-client-secret',
        'mode': 'sandbox',  # change to 'live'
        'currency': 'USD',
        'countries': ['USA', 'GBR', 'CAN', 'AUS', 'DEU', 'FRA', 'ITA', 'ESP'],
        'api_url': 'https://api-m.sandbox.paypal.com',
    },
    'mpesa': {
        'consumer_key': 'your_mpesa_consumer_key_here',
        'consumer_secret': 'your_mpesa_consumer_secret_here',
        'business_short_code': 'your_business_short_code',
        'passkey': 'your_mpesa_passkey_here',
        'currency': 'KES',
        'mode': 'sandbox',
        'countries': ['KEN'],
        'api_url': 'https://sandbox.safaricom.co.ke',
    },
    'ecocash': {
        'merchant_code': 'test-merchant',
        'api_key': 'your_ecocash_api_key_here',
        'currency': 'USD',  # EcoCash operates in USD in Zimbabwe
        'mode': 'test',
        'countries': ['ZWE'],
        'api_url': 'https://api.sandbox.ecocash.co.zw/',
    },
    'onemoney': {
        'merchant_code': 'test-merchant',
        'api_key': 'your_onemoney_api_key_here',
        'currency': 'USD',
        'mode': 'test',
        'countries': ['ZWE'],
        'api_url': 'https://sandbox.onemoney.co.zw/api/',
    },
    'razorpay': {
        'key_id': 'rzp_test_your_key_id_here',
        'key_secret': 'your_razorpay_key_secret_here',
        'currency': 'INR',
        'mode': 'test',
        'countries': ['IND'],
        'api_url': 'https://api.razorpay.com/v1',
    },
    'payu': {
        'merchant_key': 'your_payu_merchant_key_here',
        'salt': 'your_payu_salt_here',
        'currency': 'ZAR',
        'mode': 'test',
        'countries': ['ZAF'],
        'api_url': 'https://secure.payu.co.za/api',
    },
    'ozow': {
        'site_code': 'your_ozow_site_code_here',
        'private_key': 'your_ozow_private_key_here',
        'api_key': 'your_ozow_api_key_here',
        'currency': 'ZAR',
        'mode': 'test',
        'countries': ['ZAF'],
        'api_url': 'https://api.ozow.com',
    },
    'wave': {
        'api_secret': 'your_wave_api_secret_here',
        'currency': 'XOF',  # West African CFA franc
        'mode': 'test',
        'countries': ['SEN', 'CIV', 'BFA', 'MLI'],
        'api_url': 'https://api.wave.com',
    },
    'pesapal': {
        'consumer_key': 'your_pesapal_consumer_key_here',
        'consumer_secret': 'your_pesapal_consumer_secret_here',
        'currency': 'USD',
        'mode': 'demo',
        'countries': ['KEN', 'UGA', 'TZA', 'RWA', 'MWI', 'ZMB'],
        'api_url': 'https://cybqa.pesapal.com/pesapalv3/api',
    },
}


# === CURRENCY CONVERSION ===
DEFAULT_CURRENCY = 'USD'
SUPPORTED_CURRENCIES = ['USD', 'ZWL', 'ZAR', 'NGN', 'GBP', 'EUR']
CURRENCY_CONVERSION_API_URL = 'https://api.exchangeratesapi.io/latest'  # Free for dev, use premium for live

# === FEATURE TOGGLES (OWNER-CONTROLLED) ===
AVAILABLE_FEATURES = {
    'basic_dashboard': {
        'name': 'Basic Dashboard',
        'description': 'Basic school management dashboard',
        'requires_subscription': 'free',
        'category': 'core',
    },
    'premium_dashboard': {
        'name': 'Premium Dashboard',
        'description': 'Advanced analytics and reporting dashboard',
        'requires_subscription': 'premium',
        'category': 'analytics',
    },
    'ai_reports': {
        'name': 'AI-Powered Reports',
        'description': 'AI-generated student performance reports',
        'requires_subscription': 'premium',
        'category': 'ai',
    },
    'ai_chat': {
        'name': 'AI Chat Assistant',
        'description': 'AI-powered chat assistance for school management',
        'requires_subscription': 'premium',
        'category': 'ai',
    },
    'advanced_messaging': {
        'name': 'Advanced Messaging',
        'description': 'Multi-language messaging with templates',
        'requires_subscription': 'premium',
        'category': 'communication',
    },
    'multi_currency': {
        'name': 'Multi-Currency Support',
        'description': 'Accept payments in multiple currencies',
        'requires_subscription': 'premium',
        'category': 'payments',
    },
    'bulk_sms': {
        'name': 'Bulk SMS',
        'description': 'Send bulk SMS to parents and students',
        'requires_subscription': 'premium',
        'category': 'communication',
    },
    'attendance_tracking': {
        'name': 'Attendance Tracking',
        'description': 'Student and staff attendance management',
        'requires_subscription': 'free',
        'category': 'core',
    },
    'grade_management': {
        'name': 'Grade Management',
        'description': 'Student grading and report cards',
        'requires_subscription': 'free',
        'category': 'core',
    },
    'parent_portal': {
        'name': 'Parent Portal',
        'description': 'Parent access to student information',
        'requires_subscription': 'free',
        'category': 'core',
    },
    'student_portal': {
        'name': 'Student Portal',
        'description': 'Student access to assignments and grades',
        'requires_subscription': 'free',
        'category': 'core',
    },
    'teacher_portal': {
        'name': 'Teacher Portal',
        'description': 'Teacher classroom management tools',
        'requires_subscription': 'free',
        'category': 'core',
    },
    'library_management': {
        'name': 'Library Management',
        'description': 'Book tracking and library operations',
        'requires_subscription': 'premium',
        'category': 'management',
    },
    'hostel_management': {
        'name': 'Hostel Management',
        'description': 'Student accommodation management',
        'requires_subscription': 'premium',
        'category': 'management',
    },
    'transport_management': {
        'name': 'Transport Management',
        'description': 'School bus and transport tracking',
        'requires_subscription': 'premium',
        'category': 'management',
    },
    'fee_management': {
        'name': 'Fee Management',
        'description': 'School fee collection and tracking',
        'requires_subscription': 'free',
        'category': 'financial',
    },
    'payroll': {
        'name': 'Staff Payroll',
        'description': 'Staff salary and payroll management',
        'requires_subscription': 'premium',
        'category': 'hr',
    },
    'hr_management': {
        'name': 'HR Management',
        'description': 'Staff recruitment and management',
        'requires_subscription': 'premium',
        'category': 'hr',
    },
    'examination_system': {
        'name': 'Examination System',
        'description': 'Online examination and testing',
        'requires_subscription': 'premium',
        'category': 'academic',
    },
    'assignment_system': {
        'name': 'Assignment System',
        'description': 'Online assignment submission and grading',
        'requires_subscription': 'premium',
        'category': 'academic',
    },
    'timetable_management': {
        'name': 'Timetable Management',
        'description': 'Class scheduling and timetable generation',
        'requires_subscription': 'free',
        'category': 'academic',
    },
    'inventory_management': {
        'name': 'Inventory Management',
        'description': 'School asset and inventory tracking',
        'requires_subscription': 'premium',
        'category': 'management',
    },
    'certificate_generation': {
        'name': 'Certificate Generation',
        'description': 'Automated certificate and transcript generation',
        'requires_subscription': 'premium',
        'category': 'academic',
    },
    'mobile_app': {
        'name': 'Mobile App Access',
        'description': 'Mobile application for parents and students',
        'requires_subscription': 'premium',
        'category': 'mobile',
    },
    'api_access': {
        'name': 'API Access',
        'description': 'Third-party integration API access',
        'requires_subscription': 'premium',
        'category': 'integration',
    },
    'custom_reports': {
        'name': 'Custom Reports',
        'description': 'Generate custom reports and analytics',
        'requires_subscription': 'premium',
        'category': 'analytics',
    },
    'backup_restore': {
        'name': 'Backup & Restore',
        'description': 'Automated backup and data recovery',
        'requires_subscription': 'premium',
        'category': 'security',
    },
    'audit_logs': {
        'name': 'Audit Logs',
        'description': 'Comprehensive activity logging',
        'requires_subscription': 'premium',
        'category': 'security',
    },
    'data_export': {
        'name': 'Data Export',
        'description': 'Export school data in various formats',
        'requires_subscription': 'premium',
        'category': 'data',
    },
    'gdpr_compliance': {
        'name': 'GDPR Compliance',
        'description': 'GDPR compliance tools and data protection',
        'requires_subscription': 'premium',
        'category': 'compliance',
    },
}
# === SUBSCRIPTION TIERS ===
SUBSCRIPTION_TIERS = {
    'free': {
        'name': 'Free Plan',
        'price': 0,
        'currency': 'USD',
        'features': [
            'basic_dashboard', 'attendance_tracking', 'grade_management', 
            'parent_portal', 'student_portal', 'teacher_portal', 
            'fee_management', 'timetable_management'
        ],
        'ai_access': False,
        'max_students': 100,
        'max_teachers': 10,
        'storage_gb': 1,
        'description': 'Perfect for small schools getting started with basic features.',
    },
    'starter': {
        'name': 'Starter Plan',
        'price': 29,
        'currency': 'USD',
        'features': [
            'basic_dashboard', 'premium_dashboard', 'attendance_tracking', 
            'grade_management', 'parent_portal', 'student_portal', 
            'teacher_portal', 'fee_management', 'timetable_management',
            'advanced_messaging', 'bulk_sms', 'library_management'
        ],
        'ai_access': False,
        'max_students': 500,
        'max_teachers': 25,
        'storage_gb': 5,
        'description': 'Ideal for growing schools with advanced messaging and management.',
    },
    'professional': {
        'name': 'Professional Plan',
        'price': 79,
        'currency': 'USD',
        'features': [
            'basic_dashboard', 'premium_dashboard', 'ai_reports', 'ai_chat',
            'attendance_tracking', 'grade_management', 'parent_portal', 
            'student_portal', 'teacher_portal', 'fee_management', 
            'timetable_management', 'advanced_messaging', 'bulk_sms',
            'library_management', 'hostel_management', 'transport_management',
            'examination_system', 'assignment_system', 'inventory_management',
            'certificate_generation', 'custom_reports', 'multi_currency'
        ],
        'ai_access': True,
        'max_students': 2000,
        'max_teachers': 100,
        'storage_gb': 25,
        'description': 'Complete solution with AI features for established schools.',
    },
    'enterprise': {
        'name': 'Enterprise Plan',
        'price': 199,
        'currency': 'USD',
        'features': [
            # All features enabled
            'basic_dashboard', 'premium_dashboard', 'ai_reports', 'ai_chat',
            'advanced_messaging', 'multi_currency', 'bulk_sms', 'attendance_tracking',
            'grade_management', 'parent_portal', 'student_portal', 'teacher_portal',
            'library_management', 'hostel_management', 'transport_management',
            'fee_management', 'payroll', 'hr_management', 'examination_system',
            'assignment_system', 'timetable_management', 'inventory_management',
            'certificate_generation', 'mobile_app', 'api_access', 'custom_reports',
            'backup_restore', 'audit_logs', 'data_export', 'gdpr_compliance'
        ],
        'ai_access': True,
        'max_students': -1,  # Unlimited
        'max_teachers': -1,  # Unlimited
        'storage_gb': 100,
        'description': 'Unlimited access with all features for large institutions.',
    }
}

DEFAULT_TIER = 'free'
PREMIUM_TIER = 'professional'
AUTO_ACTIVATE_ON_PAYMENT = True  # instantly upgrades user tier on payment webhook

# === MULTI-TENANT SETTINGS ===
TENANT_MODEL = 'core.Tenant'
TENANT_DOMAIN_FUNCTION = 'core.utils.get_tenant_domain_model'

# Owner can create unlimited tenants, others are restricted
MAX_TENANTS_PER_USER = {
    'owner': -1,  # Unlimited for Uncle-T36
    'admin': 1,   # School admins can have 1 tenant
    'default': 0, # Regular users cannot create tenants
}

# === REGULATORY COMPLIANCE ===
GDPR_SETTINGS = {
    'enabled': True,
    'consent_required': True,
    'data_retention_days': 2555,  # 7 years
    'cookie_consent': True,
    'right_to_be_forgotten': True,
    'data_portability': True,
}

AUDIT_SETTINGS = {
    'enabled': True,
    'log_all_requests': False,  # Only log important actions
    'retention_days': 2555,     # 7 years for compliance
    'log_sensitive_data': False,
    'encrypt_logs': True,
}

# === SECURITY SETTINGS ===
SECURITY_SETTINGS = {
    'enforce_2fa': False,  # Can be enabled per tenant
    'password_complexity': True,
    'session_timeout_minutes': 480,  # 8 hours
    'max_login_attempts': 5,
    'lockout_duration_minutes': 30,
    'require_https': True,  # In production
}

# === API SETTINGS ===
API_SETTINGS = {
    'rate_limit': '1000/hour',
    'authentication_required': True,
    'api_key_required': True,
    'webhook_verification': True,
    'cors_allowed_origins': [],  # Owner configurable
}

# === INTEGRATION SETTINGS ===
INTEGRATION_SETTINGS = {
    'ministry_apis': {
        'enabled': False,  # Owner must enable
        'endpoints': {},   # Country-specific endpoints
    },
    'edtech_tools': {
        'enabled': False,  # Owner must enable
        'supported': ['google_classroom', 'microsoft_teams', 'zoom', 'canvas', 'moodle'],
    },
    'mobile_app': {
        'enabled': False,  # Owner must enable
        'push_notifications': True,
        'offline_sync': True,
    },
}

# === CLOUD AND SCALABILITY ===
CLOUD_SETTINGS = {
    'multi_region': False,  # Owner configurable
    'auto_backup': True,
    'backup_frequency': 'daily',
    'disaster_recovery': False,  # Owner configurable
    'cdn_enabled': False,       # Owner configurable
    'auto_scaling': False,      # Owner configurable
}

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
