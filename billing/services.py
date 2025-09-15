import requests
import json
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Currency, Payment, Subscription, WebhookEvent, UserProfile, NotificationLog, MessageTemplate

logger = logging.getLogger(__name__)


class CurrencyService:
    """Service for currency conversion and exchange rate management"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'EXCHANGE_RATE_API_KEY', None)
        self.base_url = 'https://api.exchangerate-api.com/v4/latest/USD'
    
    def update_exchange_rates(self):
        """Update exchange rates from external API"""
        try:
            response = requests.get(self.base_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            rates = data.get('rates', {})
            
            for currency in Currency.objects.filter(is_active=True):
                if currency.code == 'USD':
                    currency.exchange_rate_to_usd = Decimal('1.0')
                elif currency.code in rates:
                    # API gives rates from USD, we need rate TO USD
                    currency.exchange_rate_to_usd = Decimal('1') / Decimal(str(rates[currency.code]))
                
                currency.updated_at = timezone.now()
                currency.save()
            
            logger.info("Exchange rates updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update exchange rates: {str(e)}")
            return False
    
    def convert_to_usd(self, amount, currency_code):
        """Convert amount from given currency to USD"""
        try:
            if currency_code == 'USD':
                return amount
            
            currency = Currency.objects.get(code=currency_code, is_active=True)
            return amount * currency.exchange_rate_to_usd
            
        except Currency.DoesNotExist:
            logger.error(f"Currency {currency_code} not found")
            return amount  # Fallback to original amount
    
    def get_supported_currencies(self):
        """Get list of supported currencies"""
        return Currency.objects.filter(is_active=True).order_by('code')


class PaymentService:
    """Service for payment processing and webhook handling"""
    
    def __init__(self):
        self.currency_service = CurrencyService()
    
    def process_payment(self, user, subscription_plan, provider, amount, currency_code, metadata=None):
        """Create a new payment record"""
        try:
            currency = Currency.objects.get(code=currency_code)
            amount_usd = self.currency_service.convert_to_usd(amount, currency_code)
            
            # Create subscription first
            subscription = Subscription.objects.create(
                user=user,
                plan=subscription_plan,
                status='pending',
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=subscription_plan.duration_days)
            )
            
            # Create payment record
            payment = Payment.objects.create(
                user=user,
                subscription=subscription,
                provider=provider,
                amount=amount,
                currency=currency,
                amount_usd=amount_usd,
                exchange_rate=currency.exchange_rate_to_usd,
                status='pending',
                metadata=metadata or {}
            )
            
            return payment
            
        except Exception as e:
            logger.error(f"Failed to create payment: {str(e)}")
            return None
    
    def complete_payment(self, payment_id, provider_transaction_id=None, provider_reference=None):
        """Mark payment as completed and activate subscription"""
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            
            if provider_transaction_id:
                payment.provider_transaction_id = provider_transaction_id
            if provider_reference:
                payment.provider_reference = provider_reference
            
            payment.save()
            
            # Activate subscription
            if payment.subscription:
                payment.subscription.status = 'active'
                payment.subscription.save()
                
                # Send notification
                self._send_payment_success_notification(payment)
            
            logger.info(f"Payment {payment_id} completed successfully")
            return True
            
        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to complete payment {payment_id}: {str(e)}")
            return False
    
    def fail_payment(self, payment_id, reason=None):
        """Mark payment as failed"""
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'failed'
            payment.save()
            
            # Update subscription status
            if payment.subscription:
                payment.subscription.status = 'pending'
                payment.subscription.save()
            
            # Send failure notification
            self._send_payment_failure_notification(payment, reason)
            
            logger.info(f"Payment {payment_id} marked as failed")
            return True
            
        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to mark payment {payment_id} as failed: {str(e)}")
            return False
    
    def process_stripe_webhook(self, payload, signature):
        """Process Stripe webhook events"""
        try:
            # In a real implementation, you would verify the webhook signature
            # and process different event types
            
            event_data = json.loads(payload)
            event_type = event_data.get('type')
            
            if event_type == 'payment_intent.succeeded':
                # Handle successful payment
                payment_intent = event_data['data']['object']
                metadata = payment_intent.get('metadata', {})
                
                if 'payment_id' in metadata:
                    self.complete_payment(
                        metadata['payment_id'],
                        provider_transaction_id=payment_intent['id']
                    )
            
            elif event_type == 'payment_intent.payment_failed':
                # Handle failed payment
                payment_intent = event_data['data']['object']
                metadata = payment_intent.get('metadata', {})
                
                if 'payment_id' in metadata:
                    self.fail_payment(
                        metadata['payment_id'],
                        reason=payment_intent.get('last_payment_error', {}).get('message')
                    )
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Stripe webhook processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_paypal_webhook(self, payload):
        """Process PayPal webhook events"""
        try:
            event_type = payload.get('event_type')
            
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                # Handle successful payment
                resource = payload['resource']
                custom_id = resource.get('custom_id')  # Our payment ID
                
                if custom_id:
                    self.complete_payment(
                        custom_id,
                        provider_transaction_id=resource['id']
                    )
            
            elif event_type == 'PAYMENT.CAPTURE.DENIED':
                # Handle failed payment
                resource = payload['resource']
                custom_id = resource.get('custom_id')
                
                if custom_id:
                    self.fail_payment(
                        custom_id,
                        reason=resource.get('reason_code')
                    )
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"PayPal webhook processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_mobile_money_webhook(self, payload, provider_type):
        """Process Mobile Money webhook events (EcoCash, OneMoney, etc.)"""
        try:
            # Different mobile money providers have different webhook formats
            # This is a generic implementation
            
            status = payload.get('status', '').lower()
            transaction_id = payload.get('transaction_id')
            reference = payload.get('reference')  # Our payment ID
            
            if status == 'success' and reference:
                self.complete_payment(
                    reference,
                    provider_transaction_id=transaction_id
                )
            elif status in ['failed', 'cancelled'] and reference:
                self.fail_payment(
                    reference,
                    reason=payload.get('error_message')
                )
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Mobile Money webhook processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_payment_success_notification(self, payment):
        """Send payment success notification"""
        notification_service = NotificationService()
        notification_service.send_payment_notification(
            payment.user,
            'payment_success',
            {
                'amount': payment.amount,
                'currency': payment.currency.code,
                'plan_name': payment.subscription.plan.name if payment.subscription else 'N/A',
                'transaction_id': payment.provider_transaction_id
            }
        )
    
    def _send_payment_failure_notification(self, payment, reason=None):
        """Send payment failure notification"""
        notification_service = NotificationService()
        notification_service.send_payment_notification(
            payment.user,
            'payment_failed',
            {
                'amount': payment.amount,
                'currency': payment.currency.code,
                'reason': reason or 'Payment processing failed'
            }
        )


class NotificationService:
    """Service for sending notifications via SMS, email, and in-app"""
    
    def send_payment_notification(self, user, message_type, context):
        """Send payment-related notifications in user's preferred language"""
        try:
            profile = UserProfile.objects.get_or_create(user=user)[0]
            language = profile.preferred_language
            
            # Send via all channels
            self._send_email_notification(user, message_type, language, context)
            self._send_sms_notification(user, message_type, language, context)
            self._send_inapp_notification(user, message_type, language, context)
            
        except Exception as e:
            logger.error(f"Failed to send notification to {user.username}: {str(e)}")
    
    def _send_email_notification(self, user, message_type, language, context):
        """Send email notification"""
        try:
            template = MessageTemplate.objects.get(
                message_type=message_type,
                channel='email',
                language=language,
                is_active=True
            )
            
            # Format the content with context variables
            content = template.content.format(**context)
            subject = template.subject.format(**context) if template.subject else ''
            
            # In a real implementation, you would use Django's email backend
            # or a service like SendGrid, Mailgun, etc.
            
            # Log the notification
            NotificationLog.objects.create(
                user=user,
                template=template,
                channel='email',
                recipient=user.email,
                content=content,
                status='sent'
            )
            
            logger.info(f"Email notification sent to {user.email}")
            
        except MessageTemplate.DoesNotExist:
            logger.warning(f"Email template not found: {message_type}-{language}")
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
    
    def _send_sms_notification(self, user, message_type, language, context):
        """Send SMS notification"""
        try:
            profile = UserProfile.objects.get_or_create(user=user)[0]
            if not profile.phone_number:
                return
            
            template = MessageTemplate.objects.get(
                message_type=message_type,
                channel='sms',
                language=language,
                is_active=True
            )
            
            # Format the content with context variables
            content = template.content.format(**context)
            
            # In a real implementation, you would use an SMS service
            # like Twilio, Africa's Talking, etc.
            
            # Log the notification
            NotificationLog.objects.create(
                user=user,
                template=template,
                channel='sms',
                recipient=profile.phone_number,
                content=content,
                status='sent'
            )
            
            logger.info(f"SMS notification sent to {profile.phone_number}")
            
        except MessageTemplate.DoesNotExist:
            logger.warning(f"SMS template not found: {message_type}-{language}")
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
    
    def _send_inapp_notification(self, user, message_type, language, context):
        """Send in-app notification"""
        try:
            template = MessageTemplate.objects.get(
                message_type=message_type,
                channel='in_app',
                language=language,
                is_active=True
            )
            
            # Format the content with context variables
            content = template.content.format(**context)
            
            # Log the notification
            NotificationLog.objects.create(
                user=user,
                template=template,
                channel='in_app',
                recipient=user.username,
                content=content,
                status='sent'
            )
            
            logger.info(f"In-app notification created for {user.username}")
            
        except MessageTemplate.DoesNotExist:
            logger.warning(f"In-app template not found: {message_type}-{language}")
        except Exception as e:
            logger.error(f"Failed to create in-app notification: {str(e)}")
    
    def send_mass_message(self, users, message_type, context, channels=None):
        """Send mass messages to multiple users"""
        if channels is None:
            channels = ['email', 'sms', 'in_app']
        
        for user in users:
            try:
                profile = UserProfile.objects.get_or_create(user=user)[0]
                language = profile.preferred_language
                
                if 'email' in channels:
                    self._send_email_notification(user, message_type, language, context)
                if 'sms' in channels:
                    self._send_sms_notification(user, message_type, language, context)
                if 'in_app' in channels:
                    self._send_inapp_notification(user, message_type, language, context)
                    
            except Exception as e:
                logger.error(f"Failed to send mass message to {user.username}: {str(e)}")
        
        logger.info(f"Mass message sent to {len(users)} users")