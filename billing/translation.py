from django.conf import settings
import os


class ZimbabweanTranslationService:
    """Simple translation service for Zimbabwe languages"""
    
    def __init__(self):
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translations from text files"""
        for lang_code in settings.DEFAULT_LANGUAGES:
            lang_file = settings.LANGUAGE_TEMPLATES.get(lang_code)
            if lang_file and os.path.exists(lang_file):
                self.translations[lang_code] = {}
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                self.translations[lang_code][key.strip()] = value.strip()
                except Exception as e:
                    print(f"Error loading translations for {lang_code}: {e}")
    
    def translate(self, key: str, language: str = 'en') -> str:
        """Translate a key to specified language"""
        if language in self.translations and key in self.translations[language]:
            return self.translations[language][key]
        
        # Fallback to English
        if 'en' in self.translations and key in self.translations['en']:
            return self.translations['en'][key]
        
        # Last resort: return the key itself
        return key.replace('_', ' ').title()
    
    def get_language_choices(self) -> list:
        """Get available language choices"""
        return [
            ('en', 'English'),
            ('sn', 'Shona'),
            ('nd', 'Ndebele'),
        ]
    
    def detect_user_language(self, user) -> str:
        """Detect user's preferred language"""
        # Try to get from user profile
        if hasattr(user, 'profile') and hasattr(user.profile, 'preferred_language'):
            return user.profile.preferred_language
        
        # Default to English
        return 'en'


# Global translation service instance
translator = ZimbabweanTranslationService()


def get_translated_text(key: str, language: str = 'en') -> str:
    """Helper function to get translated text"""
    return translator.translate(key, language)


def get_billing_messages(language: str = 'en') -> dict:
    """Get all billing-related messages for a language"""
    billing_keys = [
        'billing_dashboard', 'current_subscription', 'upgrade_subscription',
        'payment_history', 'subscription_status', 'payment_methods',
        'mobile_money', 'credit_card', 'demo_mode_warning',
        'upgrade_to_premium', 'ai_features_available', 'basic_features',
        'select_currency', 'select_payment_method', 'billing_cycle',
        'monthly', 'annual', 'zimbabwe_optimized', 'multi_currency_support',
        'mobile_money_payments', 'local_pricing', 'subscription_upgraded',
        'payment_failed', 'access_denied', 'owner_only'
    ]
    
    return {key: translator.translate(key, language) for key in billing_keys}