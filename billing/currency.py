import requests
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import Currency
import logging

logger = logging.getLogger(__name__)


class CurrencyConversionError(Exception):
    """Exception for currency conversion errors"""
    pass


class CurrencyConverter:
    """Service for currency conversion"""
    
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str) -> Decimal:
        """
        Get exchange rate between two currencies
        Returns rate where: from_amount * rate = to_amount
        """
        if from_currency == to_currency:
            return Decimal('1.0')
        
        # Try to get from cache first
        cache_key = f"exchange_rate_{from_currency}_{to_currency}"
        cached_rate = cache.get(cache_key)
        if cached_rate:
            return Decimal(str(cached_rate))
        
        # Try to get from database first
        try:
            from_curr = Currency.objects.get(code=from_currency, is_active=True)
            to_curr = Currency.objects.get(code=to_currency, is_active=True)
            
            # Convert via USD rates
            if from_currency == 'USD':
                rate = Decimal('1.0') / to_curr.exchange_rate_to_usd
            elif to_currency == 'USD':
                rate = from_curr.exchange_rate_to_usd
            else:
                # Convert from -> USD -> to
                usd_rate_from = from_curr.exchange_rate_to_usd
                usd_rate_to = to_curr.exchange_rate_to_usd
                rate = usd_rate_from / usd_rate_to
            
            # Cache the result
            cache.set(cache_key, float(rate), cls.CACHE_TIMEOUT)
            return rate
            
        except Currency.DoesNotExist:
            logger.error(f"Currency not found: {from_currency} or {to_currency}")
            # Fall back to API
            return cls._fetch_from_api(from_currency, to_currency)
    
    @classmethod
    def _fetch_from_api(cls, from_currency: str, to_currency: str) -> Decimal:
        """Fetch exchange rate from external API"""
        try:
            # This is a simplified implementation
            # In production, you'd use a proper currency API like:
            # - exchangeratesapi.io
            # - fixer.io
            # - Open Exchange Rates
            
            api_url = settings.CURRENCY_CONVERSION_API_URL
            response = requests.get(f"{api_url}?base={from_currency}&symbols={to_currency}")
            response.raise_for_status()
            
            data = response.json()
            rate = Decimal(str(data['rates'][to_currency]))
            
            # Cache the result
            cache_key = f"exchange_rate_{from_currency}_{to_currency}"
            cache.set(cache_key, float(rate), cls.CACHE_TIMEOUT)
            
            return rate
            
        except Exception as e:
            logger.error(f"Failed to fetch exchange rate from API: {e}")
            # Return a default rate to prevent complete failure
            if from_currency == 'USD' and to_currency == 'ZWL':
                return Decimal('25.0')  # Approximate USD to ZWL rate
            elif from_currency == 'ZWL' and to_currency == 'USD':
                return Decimal('0.04')  # Approximate ZWL to USD rate
            else:
                raise CurrencyConversionError(f"Cannot get exchange rate for {from_currency} to {to_currency}")
    
    @classmethod
    def convert_amount(cls, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        rate = cls.get_exchange_rate(from_currency, to_currency)
        converted = amount * rate
        
        # Round to 2 decimal places for most currencies
        return converted.quantize(Decimal('0.01'))
    
    @classmethod
    def get_localized_amount(cls, amount: Decimal, currency_code: str, 
                           user_preferred_currency: str = None) -> dict:
        """
        Get amount in both original and user's preferred currency
        Returns dict with original and converted amounts
        """
        result = {
            'original_amount': amount,
            'original_currency': currency_code,
            'display_amount': amount,
            'display_currency': currency_code,
        }
        
        if user_preferred_currency and user_preferred_currency != currency_code:
            try:
                converted_amount = cls.convert_amount(amount, currency_code, user_preferred_currency)
                result.update({
                    'display_amount': converted_amount,
                    'display_currency': user_preferred_currency,
                    'conversion_rate': cls.get_exchange_rate(currency_code, user_preferred_currency)
                })
            except CurrencyConversionError:
                # Keep original if conversion fails
                pass
        
        return result
    
    @classmethod
    def update_exchange_rates(cls):
        """Update exchange rates in database from API"""
        logger.info("Updating exchange rates from API")
        
        try:
            # Get all active currencies except USD (which is the base)
            currencies = Currency.objects.filter(is_active=True).exclude(code='USD')
            
            for currency in currencies:
                try:
                    rate = cls._fetch_from_api('USD', currency.code)
                    currency.exchange_rate_to_usd = Decimal('1.0') / rate
                    currency.save()
                    logger.info(f"Updated {currency.code} rate: {currency.exchange_rate_to_usd}")
                    
                except Exception as e:
                    logger.error(f"Failed to update rate for {currency.code}: {e}")
            
            logger.info("Exchange rate update completed")
            
        except Exception as e:
            logger.error(f"Exchange rate update failed: {e}")
            raise CurrencyConversionError(f"Failed to update exchange rates: {e}")


class ZimbabweanCurrencyHelper:
    """Helper for Zimbabwe-specific currency operations"""
    
    ZIMBABWE_CURRENCIES = ['ZWL', 'USD']  # USD is widely used in Zimbabwe
    
    @classmethod
    def get_preferred_payment_currencies(cls) -> list:
        """Get list of preferred currencies for payments in Zimbabwe"""
        return cls.ZIMBABWE_CURRENCIES
    
    @classmethod
    def format_zimbabwean_amount(cls, amount: Decimal, currency: str) -> str:
        """Format amount according to Zimbabwean conventions"""
        if currency == 'ZWL':
            return f"ZWL ${amount:,.2f}"
        elif currency == 'USD':
            return f"US${amount:,.2f}"
        else:
            return f"{currency} {amount:,.2f}"
    
    @classmethod
    def get_mobile_money_limits(cls, provider: str) -> dict:
        """Get transaction limits for mobile money providers"""
        limits = {
            'ecocash': {
                'min_amount': Decimal('1.00'),
                'max_amount': Decimal('5000.00'),
                'daily_limit': Decimal('20000.00'),
                'currency': 'ZWL'
            },
            'onemoney': {
                'min_amount': Decimal('1.00'),
                'max_amount': Decimal('3000.00'),
                'daily_limit': Decimal('15000.00'),
                'currency': 'ZWL'
            }
        }
        
        return limits.get(provider, {})
    
    @classmethod
    def validate_mobile_money_amount(cls, amount: Decimal, provider: str) -> bool:
        """Validate if amount is within mobile money limits"""
        limits = cls.get_mobile_money_limits(provider)
        if not limits:
            return False
        
        return (limits['min_amount'] <= amount <= limits['max_amount'])