# settings.py

INSTALLED_APPS = [
    ..., 
    'schools',
    # add any new payment/messaging apps here
]

# === PAYMENT SETTINGS ===
PAYMENT_GATEWAYS = {
    'stripe': {
        'api_key': 'sk_test_51HxxxYourTestKeyHere',
        'public_key': 'pk_test_51HxxxYourTestKeyHere',
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
AI_API_KEY = 'sk_test_ai_key'  # Add your live key here when ready

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
