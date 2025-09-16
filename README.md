# LegacyGrid School Management System

## Overview

LegacyGrid School Management System is a comprehensive platform for managing school operations, including automated email notifications, billing management, and subscription services. The system features robust security controls with owner-only access to sensitive billing and payment functions.

## 🔐 Security & Access Control

### Owner-Only Billing Access

The system implements strict access controls for billing and subscription management:

- **Authorized User**: Only `Uncle-T36` can access billing features
- **Protected Features**: Payment settings, subscription management, billing dashboard, webhook configuration
- **Access Control**: Implemented via decorators and middleware
- **Unauthorized Access**: Clear messaging and automatic redirection for non-authorized users

### Security Features

- Environment variable-based configuration for sensitive data
- Masked display of API keys in admin interfaces  
- Secure webhook handling with signature verification
- XSS and CSRF protection enabled
- Demo mode for safe testing without real payments

## 💳 Stripe Payment Integration

### Configuration

#### Environment Variables (Required for Production)

```bash
# Stripe Configuration
export STRIPE_PUBLISHABLE_KEY="pk_live_your_publishable_key"
export STRIPE_SECRET_KEY="sk_live_your_secret_key" 
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
export STRIPE_PREMIUM_PRICE_ID="price_your_premium_price_id"

# OpenAI Integration
export OPENAI_API_KEY="sk-your_openai_api_key"
```

#### Stripe Dashboard Setup

1. **Create Products and Prices**:
   - Set up your subscription products in Stripe Dashboard
   - Configure recurring billing for premium tiers
   - Note the Price IDs for configuration

2. **Webhook Configuration**:
   - **Endpoint URL**: `https://yourdomain.com/schools/billing/webhook/stripe/`
   - **Events to Monitor**:
     - `payment_intent.succeeded`
     - `invoice.payment_succeeded`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`

3. **Test vs Live Mode**:
   - Use test keys during development
   - Switch to live keys for production
   - Update `STRIPE_SETTINGS['mode']` accordingly

### Subscription Tiers

#### Free Tier
- Basic dashboard access
- Basic messaging features
- No AI access
- **Price**: Free

#### Premium Tier  
- Full dashboard access
- Advanced messaging features
- Complete AI integration
- Premium reporting
- **Price**: $29.99/month (configurable)

### Payment Security Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive configuration
3. **Validate webhook signatures** to ensure authenticity
4. **Log all payment events** for audit trails
5. **Implement proper error handling** for failed payments
6. **Regular security audits** of payment flows

## 🚀 Setup & Installation

### Prerequisites

- Python 3.8+
- Django 4.0+
- Pillow (for image handling)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Uncle-T36/legacygrid-school-management.git
   cd legacygrid-school-management
   ```

2. **Install dependencies**:
   ```bash
   pip install django pillow
   # For production, consider using requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   # Use username: Uncle-T36 for billing access
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## 📧 Email System Setup

### SMTP Configuration

1. Fill in your SMTP credentials in `smtp_config_example.py`
2. Add/edit templates in the `templates/` directory  
3. Use `auto_emailer.py` to send emails for different events

### Example Usage

```python
from auto_emailer import send_event_email
from smtp_config_example import smtp_cfg

send_event_email(
    "payment_received",
    {
        "student_name": "Jane Doe",
        "parent_name": "John Doe", 
        "amount": "500",
        "date": "2025-09-15"
    },
    "parent@email.com",
    "your@email.com",
    smtp_cfg
)
```

## 🔧 Application Structure

### Core Components

- **Schools App**: Main application with school management
- **Billing System**: Owner-only payment and subscription management
- **Email System**: Automated notifications with multi-language support  
- **Access Control**: Decorator-based security for sensitive features

### Key URLs

- `/schools/profile/` - School profile management
- `/schools/billing/` - Billing dashboard (owner-only)
- `/schools/billing/subscriptions/` - Subscription management (owner-only)
- `/schools/billing/settings/` - Payment configuration (owner-only)
- `/schools/billing/webhook/stripe/` - Stripe webhook endpoint

### Access Control Implementation

```python
from schools.decorators import billing_access_required, owner_required

@billing_access_required
def billing_dashboard(request):
    # Only Uncle-T36 can access this view
    pass

@owner_required
def sensitive_feature(request):
    # Configurable owner-only access
    pass
```

## 🛡️ Security Best Practices

### For Development

- Always use test/sandbox modes for payment gateways
- Never use production API keys in development
- Keep demo mode enabled until ready for production
- Test access controls with different user accounts

### For Production

- Use strong, unique secret keys
- Enable HTTPS/TLS encryption
- Set up proper monitoring and logging
- Regular security updates and patches
- Backup sensitive configuration data
- Monitor webhook endpoints for suspicious activity

### Environment Variables Security

```bash
# Development
export DJANGO_ENV="development"
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_SECRET_KEY="sk_test_..."

# Production  
export DJANGO_ENV="production"
export STRIPE_PUBLISHABLE_KEY="pk_live_..."
export STRIPE_SECRET_KEY="sk_live_..."
```

## 🔄 Multi-Currency Support

The system supports multiple currencies for international deployments:

- **Default**: USD
- **Supported**: USD, ZWL, ZAR, NGN, GBP, EUR
- **Conversion**: Real-time exchange rates via API
- **Local Payment**: Zimbabwe mobile money integration (EcoCash, OneMoney)

## 📱 Multi-Language Support

- **English** (en) - Primary language
- **Shona** (sn) - Local language support
- **Ndebele** (nd) - Regional language support

## 🐛 Error Logging

All errors are logged in `email_error.log`. Monitor this file for:
- SMTP connection issues
- Payment processing errors  
- Webhook delivery failures
- Access control violations

## 🧪 Testing

### Running Tests

```bash
# Test email system
python test_auto_emailer.py

# Test Django application
python manage.py test

# Check system configuration
python manage.py check
```

### Access Control Testing

1. Create test users with different permissions
2. Attempt to access billing URLs with non-owner accounts
3. Verify proper redirection and error messages
4. Test webhook endpoints with invalid signatures

## 📚 Extending the System

### Adding New Payment Gateways

1. Update `PAYMENT_GATEWAYS` in settings
2. Implement gateway-specific logic in views
3. Add webhook handling for new provider
4. Update templates for gateway selection

### Adding New Email Templates

1. Create template files in `templates/` directory
2. Map new events in `TEMPLATE_MAP` in `auto_emailer.py`
3. Test template rendering with sample data

### Customizing Access Control

1. Modify `BILLING_ACCESS_CONTROL` settings
2. Update decorators in `schools/decorators.py`
3. Customize unauthorized templates
4. Test with different user roles

## 📞 Support & Documentation

- **Documentation**: [GitHub Repository](https://github.com/Uncle-T36/legacygrid-school-management)
- **Support Email**: support@legacygrid.co.zw
- **Issues**: GitHub Issues for bug reports and feature requests

## 📄 License & Contributing

Please refer to the repository for licensing information and contribution guidelines.

---

**⚠️ Important**: Always ensure proper testing of billing and payment features before deploying to production. The owner-only access controls are critical for maintaining system security and should not be bypassed or disabled without proper authorization.