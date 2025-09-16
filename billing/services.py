from django.utils import timezone
from django.conf import settings
from django.db import transaction
from datetime import datetime, timedelta
from .models import (
    UserSubscription, SubscriptionTier, Payment, 
    BillingAuditLog, PaymentProvider
)
from .gateways import PaymentGatewayFactory
from .currency import CurrencyConverter
import logging

logger = logging.getLogger(__name__)


class SubscriptionError(Exception):
    """Base exception for subscription errors"""
    pass


class SubscriptionManager:
    """Service for managing user subscriptions"""
    
    @classmethod
    def create_subscription(cls, user, tier_name: str, billing_cycle: str = 'monthly',
                          currency_code: str = 'USD', payment_provider: str = None) -> UserSubscription:
        """Create a new subscription for a user"""
        
        try:
            tier = SubscriptionTier.objects.get(name=tier_name, is_active=True)
        except SubscriptionTier.DoesNotExist:
            raise SubscriptionError(f"Subscription tier '{tier_name}' not found")
        
        try:
            from .models import Currency
            currency = Currency.objects.get(code=currency_code, is_active=True)
        except Currency.DoesNotExist:
            raise SubscriptionError(f"Currency '{currency_code}' not found")
        
        # Calculate expiration date
        if billing_cycle == 'monthly':
            expires_at = timezone.now() + timedelta(days=30)
        elif billing_cycle == 'annual':
            expires_at = timezone.now() + timedelta(days=365)
        else:
            raise SubscriptionError(f"Invalid billing cycle: {billing_cycle}")
        
        # Create or update subscription
        subscription, created = UserSubscription.objects.update_or_create(
            user=user,
            defaults={
                'tier': tier,
                'billing_cycle': billing_cycle,
                'currency': currency,
                'expires_at': expires_at,
                'status': 'pending',
                'payment_provider': payment_provider or '',
            }
        )
        
        # Log the action
        BillingAuditLog.objects.create(
            user=user,
            action='subscription_created',
            description=f"Subscription created for tier '{tier_name}' with {billing_cycle} billing",
            metadata={
                'tier': tier_name,
                'billing_cycle': billing_cycle,
                'currency': currency_code,
                'expires_at': expires_at.isoformat(),
            }
        )
        
        logger.info(f"Created subscription for user {user.username}: {tier_name} ({billing_cycle})")
        return subscription
    
    @classmethod
    def activate_subscription(cls, subscription: UserSubscription, payment_id: str = None):
        """Activate a subscription"""
        with transaction.atomic():
            subscription.status = 'active'
            subscription.save()
            
            BillingAuditLog.objects.create(
                user=subscription.user,
                action='subscription_updated',
                description=f"Subscription activated for tier '{subscription.tier.name}'",
                metadata={
                    'tier': subscription.tier.name,
                    'payment_id': payment_id,
                    'activated_at': timezone.now().isoformat(),
                }
            )
        
        logger.info(f"Activated subscription for user {subscription.user.username}")
    
    @classmethod
    def cancel_subscription(cls, subscription: UserSubscription, reason: str = None,
                          admin_user=None):
        """Cancel a subscription"""
        with transaction.atomic():
            old_status = subscription.status
            subscription.status = 'cancelled'
            subscription.auto_renew = False
            subscription.save()
            
            BillingAuditLog.objects.create(
                user=subscription.user,
                admin_user=admin_user,
                action='subscription_cancelled',
                description=f"Subscription cancelled. Reason: {reason or 'Not specified'}",
                metadata={
                    'old_status': old_status,
                    'reason': reason,
                    'cancelled_at': timezone.now().isoformat(),
                }
            )
        
        logger.info(f"Cancelled subscription for user {subscription.user.username}")
    
    @classmethod
    def upgrade_subscription(cls, subscription: UserSubscription, new_tier_name: str,
                           admin_user=None) -> UserSubscription:
        """Upgrade subscription to a new tier"""
        try:
            new_tier = SubscriptionTier.objects.get(name=new_tier_name, is_active=True)
        except SubscriptionTier.DoesNotExist:
            raise SubscriptionError(f"Subscription tier '{new_tier_name}' not found")
        
        with transaction.atomic():
            old_tier = subscription.tier.name
            subscription.tier = new_tier
            subscription.save()
            
            BillingAuditLog.objects.create(
                user=subscription.user,
                admin_user=admin_user,
                action='tier_changed',
                description=f"Subscription upgraded from '{old_tier}' to '{new_tier_name}'",
                metadata={
                    'old_tier': old_tier,
                    'new_tier': new_tier_name,
                    'upgraded_at': timezone.now().isoformat(),
                }
            )
        
        logger.info(f"Upgraded subscription for user {subscription.user.username}: {old_tier} -> {new_tier_name}")
        return subscription
    
    @classmethod
    def check_expired_subscriptions(cls):
        """Check and update expired subscriptions"""
        expired_subscriptions = UserSubscription.objects.filter(
            status='active',
            expires_at__lt=timezone.now()
        )
        
        for subscription in expired_subscriptions:
            subscription.status = 'expired'
            subscription.save()
            
            BillingAuditLog.objects.create(
                user=subscription.user,
                action='subscription_updated',
                description="Subscription expired",
                metadata={
                    'tier': subscription.tier.name,
                    'expired_at': timezone.now().isoformat(),
                }
            )
            
            logger.info(f"Marked subscription as expired for user {subscription.user.username}")
    
    @classmethod
    def renew_subscription(cls, subscription: UserSubscription) -> bool:
        """Attempt to renew a subscription"""
        if not subscription.auto_renew:
            return False
        
        # Calculate new expiration date
        if subscription.billing_cycle == 'monthly':
            new_expires_at = subscription.expires_at + timedelta(days=30)
        elif subscription.billing_cycle == 'annual':
            new_expires_at = subscription.expires_at + timedelta(days=365)
        else:
            logger.error(f"Invalid billing cycle for renewal: {subscription.billing_cycle}")
            return False
        
        # In a real implementation, this would process payment first
        # For now, we'll just extend the subscription
        subscription.expires_at = new_expires_at
        subscription.status = 'active'
        subscription.save()
        
        BillingAuditLog.objects.create(
            user=subscription.user,
            action='subscription_updated',
            description=f"Subscription renewed for {subscription.billing_cycle} period",
            metadata={
                'tier': subscription.tier.name,
                'new_expires_at': new_expires_at.isoformat(),
                'billing_cycle': subscription.billing_cycle,
            }
        )
        
        logger.info(f"Renewed subscription for user {subscription.user.username}")
        return True
    
    @classmethod
    def get_user_subscription(cls, user) -> UserSubscription:
        """Get user's current subscription or create a free one"""
        try:
            return UserSubscription.objects.get(user=user)
        except UserSubscription.DoesNotExist:
            # Create free subscription
            free_tier = SubscriptionTier.objects.get(name='free')
            return cls.create_subscription(
                user=user,
                tier_name='free',
                billing_cycle='monthly'
            )


class PaymentProcessor:
    """Service for processing payments"""
    
    @classmethod
    def process_subscription_payment(cls, user, tier_name: str, billing_cycle: str,
                                   currency_code: str, payment_provider: str,
                                   payment_data: dict) -> Payment:
        """Process a subscription payment"""
        
        from .models import Currency
        
        try:
            tier = SubscriptionTier.objects.get(name=tier_name, is_active=True)
            currency = Currency.objects.get(code=currency_code, is_active=True)
            provider = PaymentProvider.objects.get(name=payment_provider, is_active=True)
        except (SubscriptionTier.DoesNotExist, Currency.DoesNotExist, PaymentProvider.DoesNotExist) as e:
            raise SubscriptionError(f"Invalid payment parameters: {e}")
        
        # Get price for the tier
        try:
            if billing_cycle == 'monthly':
                price = tier.prices.get(currency=currency).monthly_price
            elif billing_cycle == 'annual':
                price = tier.prices.get(currency=currency).annual_price
                if price is None:
                    raise SubscriptionError(f"Annual pricing not available for {tier_name}")
            else:
                raise SubscriptionError(f"Invalid billing cycle: {billing_cycle}")
        except:
            raise SubscriptionError(f"Pricing not available for {tier_name} in {currency_code}")
        
        # Create payment record
        payment = Payment.objects.create(
            user=user,
            provider=provider,
            amount=price,
            currency=currency,
            status='pending',
            metadata={
                'tier': tier_name,
                'billing_cycle': billing_cycle,
                'payment_data': payment_data,
            }
        )
        
        # Process payment through gateway
        if not settings.DEMO_MODE:
            try:
                gateway = PaymentGatewayFactory.create_gateway(
                    payment_provider,
                    settings.PAYMENT_GATEWAYS[payment_provider]
                )
                
                result = gateway.create_payment(
                    amount=price,
                    currency=currency_code,
                    customer_data={
                        'user_id': user.id,
                        'email': user.email,
                        'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                        **payment_data
                    }
                )
                
                if result.success:
                    payment.status = 'completed'
                    payment.external_payment_id = result.transaction_id
                    payment.processed_at = timezone.now()
                    
                    # Create or activate subscription
                    subscription = SubscriptionManager.create_subscription(
                        user=user,
                        tier_name=tier_name,
                        billing_cycle=billing_cycle,
                        currency_code=currency_code,
                        payment_provider=payment_provider
                    )
                    payment.subscription = subscription
                    
                    if settings.AUTO_ACTIVATE_ON_PAYMENT:
                        SubscriptionManager.activate_subscription(subscription, str(payment.id))
                    
                else:
                    payment.status = 'failed'
                    payment.metadata['error'] = result.error_message
                
                payment.save()
                
            except Exception as e:
                logger.error(f"Payment processing failed: {e}")
                payment.status = 'failed'
                payment.metadata['error'] = str(e)
                payment.save()
                raise SubscriptionError(f"Payment processing failed: {e}")
        
        else:
            # Demo mode - simulate successful payment
            payment.status = 'completed'
            payment.external_payment_id = f"demo_{payment.id}"
            payment.processed_at = timezone.now()
            
            subscription = SubscriptionManager.create_subscription(
                user=user,
                tier_name=tier_name,
                billing_cycle=billing_cycle,
                currency_code=currency_code,
                payment_provider=payment_provider
            )
            payment.subscription = subscription
            
            SubscriptionManager.activate_subscription(subscription, str(payment.id))
            payment.save()
        
        # Log the payment
        BillingAuditLog.objects.create(
            user=user,
            action='payment_created',
            description=f"Payment created for {tier_name} subscription",
            metadata={
                'payment_id': str(payment.id),
                'amount': str(price),
                'currency': currency_code,
                'provider': payment_provider,
                'status': payment.status,
            }
        )
        
        return payment