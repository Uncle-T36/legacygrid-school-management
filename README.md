# LegacyGrid School Management System

A comprehensive school management system with automated email notifications, billing management, and subscription services. Features strict owner-only access controls for billing and payment operations.

## Features

- **Automated Email System**: Customizable email notifications for school events (payments, registrations, etc.)
- **Secure Billing Management**: Owner-only access to billing and subscription management
- **Stripe Integration**: Full Stripe payment processing with webhook support
- **Multi-Currency Support**: USD, ZWL, ZAR, NGN, GBP, EUR
- **Subscription Tiers**: Free and Premium plans with AI features
- **Security-First**: Comprehensive access controls and audit logging

## Quick Setup

### 1. Basic Installation

```bash
# Clone the repository
git clone https://github.com/Uncle-T36/legacygrid-school-management.git
cd legacygrid-school-management

# Install dependencies
pip install django Pillow

# Run initial setup
python manage.py migrate
python manage.py collectstatic
```

### 2. Email Configuration

1. Copy `smtp_config_example.py` to `smtp_config.py`
2. Fill in your SMTP credentials:
   - **server**: Your SMTP provider (e.g., smtp.gmail.com)
   - **port**: Use 465 for SSL or 587 for TLS
   - **user**: Your sender email address
   - **password**: Your email password or app password

3. Edit templates in the `templates/` directory as needed
4. Use `auto_emailer.py` to send event-driven emails

## Stripe Payment Integration

### Stripe Configuration

The system includes comprehensive Stripe integration with secure, owner-only access controls.

#### Environment Variables (Recommended)

Set these environment variables for production:

```bash
# Stripe API Keys
export STRIPE_PUBLISHABLE_KEY="pk_live_your_publishable_key"
export STRIPE_SECRET_KEY="sk_live_your_secret_key"
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
export STRIPE_LIVE_MODE="true"

# Stripe Products and Prices
export STRIPE_PREMIUM_PRICE_ID="price_premium_monthly"
export STRIPE_PREMIUM_PRODUCT_ID="prod_premium"
```

#### Settings Configuration

In `legacygrid_school_management/settings.py`, Stripe is configured with:

```python
# Stripe settings
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_default')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_default')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_test_default')
STRIPE_LIVE_MODE = os.getenv('STRIPE_LIVE_MODE', 'False').lower() == 'true'
```

#### Subscription Tiers

Two tiers are configured:

- **Free Plan**: Basic features, no AI access ($0/month)
- **Premium Plan**: Full features with AI access ($29.99/month)

### Stripe Webhook Setup

1. In your Stripe Dashboard, go to Webhooks
2. Add endpoint: `https://yourdomain.com/schools/billing/webhook/stripe/`
3. Select events: `payment_intent.succeeded`, `customer.subscription.created`, etc.
4. Copy the webhook secret to your environment variables

## Owner-Only Access Controls

### Security Model

**CRITICAL**: All billing and subscription management is restricted to the system owner only.

- **Billing Owner**: Only the user `Uncle-T36` can access billing features
- **Access Control**: Strict decorator-based authorization
- **Audit Logging**: All billing access attempts are logged
- **Clear Messaging**: Unauthorized users receive clear denial messages

### Access Configuration

```python
# In settings.py
BILLING_OWNER_USERNAME = 'Uncle-T36'
ALLOW_ONLY_OWNER_BILLING = True
LOG_BILLING_ACCESS_ATTEMPTS = True
BILLING_SESSION_TIMEOUT = 300  # 5 minutes
```

### Protected URLs

These URLs require owner-only access:

- `/schools/billing/` - Main billing dashboard
- `/schools/billing/subscriptions/` - Subscription management
- `/schools/billing/payment-settings/` - Payment gateway configuration
- `/schools/billing/stripe-config/` - Stripe-specific settings

### Access Denied Handling

When unauthorized users attempt to access billing features:

1. **Clear Error Message**: Explains access restriction
2. **Support Information**: Provides contact details
3. **Security Logging**: Logs unauthorized access attempts
4. **User Guidance**: Redirects to appropriate resources

## Security Practices

### 1. Environment Variables

**Never commit sensitive data to version control**. Use environment variables for:

- Stripe API keys
- Database credentials
- Secret keys
- Email passwords

### 2. Access Control Implementation

```python
from schools.billing_utils import billing_owner_required

@billing_owner_required
def sensitive_billing_function(request):
    # Only Uncle-T36 can access this
    pass
```

### 3. Logging and Monitoring

```python
# Billing access attempts are automatically logged
logger.info(f"Billing owner {user.username} accessed billing feature")
logger.warning(f"User {user.username} attempted unauthorized billing access")
```

### 4. Demo Mode Protection

```python
DEMO_MODE = True  # Disables real payments in development
```

## Usage Examples

### Email Notifications

```python
from auto_emailer import send_event_email
from smtp_config import smtp_cfg

# Send payment receipt
send_event_email(
    "payment_received",
    {
        "student_name": "Jane Doe",
        "parent_name": "John Doe",
        "amount": "500",
        "date": "2025-09-15"
    },
    "parent@email.com",
    "school@legacygrid.co.zw",
    smtp_cfg
)
```

### Billing Access Check

```python
from schools.billing_utils import check_billing_access

# In templates or views
if check_billing_access(request.user):
    # Show billing options
    pass
else:
    # Show access denied message
    pass
```

## Testing

### Email Testing

```bash
python run_email_test.py
```

### Django Tests

```bash
python manage.py test
```

### Access Control Testing

Test billing access controls by:

1. Logging in as a non-owner user
2. Attempting to access `/schools/billing/`
3. Verifying access denial message
4. Checking logs for security events

## Error Logging

- **Email Errors**: Logged to `email_error.log`
- **Billing Access**: Logged to `billing_access.log`
- **Django Errors**: Standard Django logging

## Production Deployment

### 1. Security Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set strong `SECRET_KEY`
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set `STRIPE_LIVE_MODE = True`

### 2. Stripe Live Mode

```bash
# Switch to live mode
export STRIPE_LIVE_MODE="true"
export STRIPE_PUBLISHABLE_KEY="pk_live_..."
export STRIPE_SECRET_KEY="sk_live_..."
```

### 3. Database Migration

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Support and Contact

- **Documentation**: [GitHub Repository](https://github.com/Uncle-T36/legacygrid-school-management)
- **Support Email**: support@legacygrid.co.zw
- **Billing Issues**: Contact Uncle-T36 directly (owner-only access)

## License

This project is proprietary software. Unauthorized access to billing features is strictly prohibited and monitored.

---

**Security Notice**: This system implements strict access controls for billing operations. All access attempts are logged and monitored. Only authorized personnel (Uncle-T36) can access billing and subscription management features.