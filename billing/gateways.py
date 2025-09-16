from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PaymentGatewayError(Exception):
    """Base exception for payment gateway errors"""
    pass


class PaymentProcessingError(PaymentGatewayError):
    """Exception for payment processing failures"""
    pass


class InvalidConfigurationError(PaymentGatewayError):
    """Exception for invalid gateway configuration"""
    pass


class PaymentResult:
    """Standard result object for payment operations"""
    
    def __init__(self, success: bool, transaction_id: str = None, 
                 error_message: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.transaction_id = transaction_id
        self.error_message = error_message
        self.metadata = metadata or {}


class PaymentGateway(ABC):
    """Abstract base class for payment gateways"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """Validate gateway configuration"""
        pass
    
    @abstractmethod
    def create_payment(self, amount: Decimal, currency: str, 
                      customer_data: Dict[str, Any]) -> PaymentResult:
        """Create a payment"""
        pass
    
    @abstractmethod
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Verify payment status"""
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, 
                      amount: Optional[Decimal] = None) -> PaymentResult:
        """Refund a payment"""
        pass
    
    @abstractmethod
    def create_subscription(self, customer_data: Dict[str, Any], 
                           plan_id: str) -> PaymentResult:
        """Create a subscription"""
        pass
    
    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> PaymentResult:
        """Cancel a subscription"""
        pass
    
    @abstractmethod
    def get_supported_currencies(self) -> list:
        """Get list of supported currencies"""
        pass
    
    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        pass


class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation"""
    
    def validate_config(self) -> None:
        required_fields = ['api_key', 'public_key']
        for field in required_fields:
            if field not in self.config:
                raise InvalidConfigurationError(f"Missing required field: {field}")
    
    def create_payment(self, amount: Decimal, currency: str, 
                      customer_data: Dict[str, Any]) -> PaymentResult:
        try:
            # In a real implementation, this would use the Stripe SDK
            logger.info(f"Creating Stripe payment: {amount} {currency}")
            
            # Simulate payment creation
            if self.config.get('mode') == 'test':
                transaction_id = f"stripe_test_{amount}_{currency}"
                return PaymentResult(
                    success=True,
                    transaction_id=transaction_id,
                    metadata={'provider': 'stripe', 'mode': 'test'}
                )
            
            # Real implementation would go here
            return PaymentResult(
                success=False,
                error_message="Live Stripe integration not implemented yet"
            )
            
        except Exception as e:
            logger.error(f"Stripe payment creation failed: {e}")
            return PaymentResult(
                success=False,
                error_message=str(e)
            )
    
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        # Implementation would query Stripe API
        logger.info(f"Verifying Stripe payment: {transaction_id}")
        return PaymentResult(success=True, transaction_id=transaction_id)
    
    def refund_payment(self, transaction_id: str, 
                      amount: Optional[Decimal] = None) -> PaymentResult:
        logger.info(f"Refunding Stripe payment: {transaction_id}")
        return PaymentResult(success=True, transaction_id=transaction_id)
    
    def create_subscription(self, customer_data: Dict[str, Any], 
                           plan_id: str) -> PaymentResult:
        logger.info(f"Creating Stripe subscription for plan: {plan_id}")
        return PaymentResult(success=True, transaction_id=f"sub_{plan_id}")
    
    def cancel_subscription(self, subscription_id: str) -> PaymentResult:
        logger.info(f"Cancelling Stripe subscription: {subscription_id}")
        return PaymentResult(success=True, transaction_id=subscription_id)
    
    def get_supported_currencies(self) -> list:
        return ['USD', 'EUR', 'GBP', 'ZAR']
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        # Would implement Stripe webhook signature verification
        return True


class PayPalGateway(PaymentGateway):
    """PayPal payment gateway implementation"""
    
    def validate_config(self) -> None:
        required_fields = ['client_id', 'client_secret']
        for field in required_fields:
            if field not in self.config:
                raise InvalidConfigurationError(f"Missing required field: {field}")
    
    def create_payment(self, amount: Decimal, currency: str, 
                      customer_data: Dict[str, Any]) -> PaymentResult:
        logger.info(f"Creating PayPal payment: {amount} {currency}")
        if self.config.get('mode') == 'sandbox':
            return PaymentResult(
                success=True,
                transaction_id=f"paypal_test_{amount}_{currency}",
                metadata={'provider': 'paypal', 'mode': 'sandbox'}
            )
        return PaymentResult(success=False, error_message="Live PayPal not implemented")
    
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        return PaymentResult(success=True, transaction_id=transaction_id)
    
    def refund_payment(self, transaction_id: str, 
                      amount: Optional[Decimal] = None) -> PaymentResult:
        return PaymentResult(success=True, transaction_id=transaction_id)
    
    def create_subscription(self, customer_data: Dict[str, Any], 
                           plan_id: str) -> PaymentResult:
        return PaymentResult(success=True, transaction_id=f"paypal_sub_{plan_id}")
    
    def cancel_subscription(self, subscription_id: str) -> PaymentResult:
        return PaymentResult(success=True, transaction_id=subscription_id)
    
    def get_supported_currencies(self) -> list:
        return ['USD', 'EUR', 'GBP']
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        return True


class MobileMoneyGateway(PaymentGateway):
    """Zimbabwe mobile money gateway (EcoCash, OneMoney)"""
    
    def validate_config(self) -> None:
        required_fields = ['merchant_code', 'api_url']
        for field in required_fields:
            if field not in self.config:
                raise InvalidConfigurationError(f"Missing required field: {field}")
    
    def create_payment(self, amount: Decimal, currency: str, 
                      customer_data: Dict[str, Any]) -> PaymentResult:
        logger.info(f"Creating mobile money payment: {amount} {currency}")
        
        # Only support ZWL for mobile money
        if currency != 'ZWL':
            return PaymentResult(
                success=False,
                error_message="Mobile money only supports ZWL currency"
            )
        
        if self.config.get('mode') == 'test':
            return PaymentResult(
                success=True,
                transaction_id=f"mobile_{self.config['merchant_code']}_{amount}",
                metadata={'provider': 'mobile_money', 'mode': 'test'}
            )
        
        return PaymentResult(success=False, error_message="Live mobile money not implemented")
    
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        return PaymentResult(success=True, transaction_id=transaction_id)
    
    def refund_payment(self, transaction_id: str, 
                      amount: Optional[Decimal] = None) -> PaymentResult:
        return PaymentResult(success=False, error_message="Mobile money refunds not supported")
    
    def create_subscription(self, customer_data: Dict[str, Any], 
                           plan_id: str) -> PaymentResult:
        return PaymentResult(success=False, error_message="Mobile money subscriptions not supported")
    
    def cancel_subscription(self, subscription_id: str) -> PaymentResult:
        return PaymentResult(success=False, error_message="Mobile money subscriptions not supported")
    
    def get_supported_currencies(self) -> list:
        return ['ZWL']
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        return True


class PaymentGatewayFactory:
    """Factory for creating payment gateway instances"""
    
    GATEWAY_CLASSES = {
        'stripe': StripeGateway,
        'paypal': PayPalGateway,
        'ecocash': MobileMoneyGateway,
        'onemoney': MobileMoneyGateway,
    }
    
    @classmethod
    def create_gateway(cls, provider_name: str, config: Dict[str, Any]) -> PaymentGateway:
        """Create a payment gateway instance"""
        if provider_name not in cls.GATEWAY_CLASSES:
            raise ValueError(f"Unsupported payment provider: {provider_name}")
        
        gateway_class = cls.GATEWAY_CLASSES[provider_name]
        return gateway_class(config)
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of supported payment providers"""
        return list(cls.GATEWAY_CLASSES.keys())