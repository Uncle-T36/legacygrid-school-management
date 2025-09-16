# LegacyGrid School Management System

A comprehensive school management system with advanced billing and subscription automation, optimized for Zimbabwean schools.

## Features

### 🏫 School Management
- School profiles and administration
- Automated email notifications for school events (payments, registrations, etc.)
- Customizable email templates

### 💳 Billing & Subscription System (NEW)
- **Multi-Currency Support**: ZWL, USD, ZAR, NGN, KES with real-time conversion
- **Payment Gateways**: Stripe, PayPal, and Zimbabwe mobile money (EcoCash, OneMoney)
- **Subscription Tiers**: Free and Premium plans with feature-based access control
- **Owner-Only Access**: Secure billing management restricted to Uncle-T36
- **Zimbabwe Localization**: Africa/Harare timezone, local payment methods, multi-language support
- **Automated Processing**: Webhook integration for instant subscription activation
- **Demo Mode**: Safe testing environment that prevents real payment processing
- **Comprehensive Analytics**: Revenue tracking, subscription metrics, payment analytics

### 🌍 Zimbabwe-Specific Features
- **Multi-Language Support**: English, Shona, Ndebele
- **Local Payment Methods**: EcoCash, OneMoney mobile money integration
- **Currency Optimization**: Zimbabwe-friendly pricing and exchange rates
- **Local Business Logic**: Handles Zimbabwe's unique payment landscape

### 🔒 Security & Access Control
- Owner-only billing access (Uncle-T36 exclusive)
- Subscription-based feature gating
- Comprehensive audit logging
- Secure webhook endpoints with signature verification

## Setup

### Basic Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install django pillow
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

4. Initialize billing system:
   ```bash
   python manage.py init_billing
   ```

5. Create superuser (billing owner):
   ```bash
   python manage.py createsuperuser
   # Username: Uncle-T36 (required for billing access)
   ```

### Email Configuration

1. Fill in your SMTP credentials in `smtp_config_example.py`
2. Add/edit templates in the `templates/` directory
3. Use `auto_emailer.py` to send emails for different events

### Billing Configuration

The billing system is pre-configured with sensible defaults for Zimbabwe:

- **Supported Currencies**: USD, ZWL, ZAR, NGN, KES
- **Payment Providers**: Stripe (test), PayPal (sandbox), EcoCash, OneMoney
- **Subscription Tiers**: Free and Premium
- **Demo Mode**: Enabled by default for safe testing

#### Production Configuration

To enable live payments, update `legacygrid_school_management/settings.py`:

```python
# Disable demo mode
DEMO_MODE = False

# Update payment gateway configurations
PAYMENT_GATEWAYS = {
    'stripe': {
        'api_key': 'sk_live_your_live_key',
        'public_key': 'pk_live_your_live_key',
        'mode': 'live',
    },
    # ... other providers
}
```

## Usage

### Email System

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
    "school@email.com",
    smtp_cfg
)
```

### Billing System

#### User Dashboard
- Visit `/billing/` to view subscription status
- Upgrade plans at `/billing/upgrade/`
- View payment history at `/billing/history/`

#### Admin Dashboard (Owner Only)
- Access at `/billing/admin/` (Uncle-T36 only)
- Manage all subscriptions and payments
- View analytics and system status
- Process bulk operations

#### API Endpoints
- Webhook handlers: `/billing/webhooks/<provider>/`
- Tier pricing: `/billing/api/tier-pricing/`

## Management Commands

### Billing System

```bash
# Initialize billing system with default data
python manage.py init_billing

# Update exchange rates
python manage.py update_exchange_rates

# Process expired subscriptions
python manage.py process_subscriptions

# Process with dry run
python manage.py process_subscriptions --dry-run
```

### Email System

```bash
# Test email configuration
python run_email_test.py

# Run email tests
python -m unittest test_auto_emailer.py
```

## File Structure

```
legacygrid-school-management/
├── auto_emailer.py              # Email automation system
├── billing/                     # Billing & subscription app
│   ├── models.py               # Database models
│   ├── views.py                # View controllers
│   ├── services.py             # Business logic
│   ├── gateways.py             # Payment gateway abstraction
│   ├── currency.py             # Currency conversion
│   ├── decorators.py           # Access control decorators
│   ├── translation.py          # Multi-language support
│   ├── templates/billing/      # HTML templates
│   └── management/commands/    # Management commands
├── schools/                     # School management app
├── templates/                   # Email and message templates
│   ├── email_*.txt             # Email templates
│   └── messages_*.txt          # Multi-language messages
└── legacygrid_school_management/
    ├── settings.py             # Django configuration
    └── urls.py                 # URL routing
```

## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Billing Tests Only
```bash
python manage.py test billing
```

### Test Coverage
The billing system includes comprehensive tests for:
- Model functionality and relationships
- Payment gateway integration
- Subscription management
- Currency conversion
- Access control and security
- Multi-language support

## Error Logging

All email errors are logged in `email_error.log`.
Billing operations are tracked in the database audit log.

## Zimbabwe Localization

### Supported Languages
- **English** (en): Default language
- **Shona** (sn): Native Zimbabwe language
- **Ndebele** (nd): Native Zimbabwe language

### Mobile Money Integration
- **EcoCash**: Zimbabwe's leading mobile money platform
- **OneMoney**: Alternative mobile money provider
- Transaction limits and validation included

### Currency Support
- **ZWL**: Zimbabwean Dollar (primary local currency)
- **USD**: US Dollar (widely accepted in Zimbabwe)
- **ZAR**: South African Rand (regional currency)
- **NGN**: Nigerian Naira (regional business)
- **KES**: Kenyan Shilling (East African trade)

## Security Considerations

### Owner-Only Access
- Billing administration restricted to `Uncle-T36` username
- All sensitive billing operations require owner authentication
- Comprehensive audit logging for all administrative actions

### Demo Mode Protection
- Prevents accidental real payment processing during development
- All payments marked as demo transactions
- Safe for testing and development

### Data Protection
- Secure webhook signature verification
- Encrypted payment data storage
- GDPR-compliant audit logging

## Extending

### Adding New Payment Providers
1. Create new gateway class in `billing/gateways.py`
2. Implement required abstract methods
3. Add provider configuration to settings
4. Register in `PaymentGatewayFactory`

### Adding New Languages
1. Create message file in `templates/messages_<lang>.txt`
2. Update `DEFAULT_LANGUAGES` in settings
3. Add language choice to translation service

### Adding New Features
1. Update subscription tier features in database
2. Use `@subscription_required` decorator for access control
3. Add feature checks in templates

## Support

- **Documentation**: This README and code comments
- **Support Email**: support@legacygrid.co.zw
- **Owner Contact**: Uncle-T36

## License

Copyright © 2025 LegacyGrid. All rights reserved.