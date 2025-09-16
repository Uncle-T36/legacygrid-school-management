# LegacyGrid School Management System

A comprehensive Django-based school management system with secure billing and subscription management.

## 🔐 Security Features

This system implements **strict owner-only access controls** for all billing and subscription management:

- **Owner-Only Access**: Only the verified owner account (`Uncle-T36`) can access billing pages
- **Secure API Key Management**: All sensitive keys stored as environment variables
- **Payment Security**: Stripe integration with test mode for safe development
- **Access Control**: Custom decorators ensure unauthorized users are blocked
- **Audit Logging**: All access attempts are monitored and logged

## 🏗️ System Architecture

### Core Applications
- **Schools**: School profile and management
- **Billing**: Secure payment and subscription management (Owner-only)

### Security Implementation
- Custom `@owner_only` decorator restricts billing access
- Automatic redirection to "Not Authorized" page for non-owners
- Environment variable protection for all sensitive credentials

## 💳 Billing & Payments

### Owner-Only Access
Only the system owner (`Uncle-T36`) can:
- View billing dashboard
- Manage subscriptions
- Configure payment settings
- Access financial data

### Stripe Integration
- **Test Mode**: Safe development environment
- **Secure Keys**: Environment variable configuration
- **Webhook Support**: Payment confirmation and validation
- **Multiple Currencies**: USD, ZWL, ZAR, NGN, GBP, EUR

### Subscription Tiers
- **Free**: Basic dashboard and messaging
- **Premium**: Full features including AI access

## 📁 Project Structure

```
legacygrid_school_management/
├── billing/                    # Owner-only billing app
│   ├── views.py               # Billing views with @owner_only decorator
│   ├── urls.py                # Billing URL routing
│   └── templates/billing/     # Secure billing templates
├── schools/                   # School management
├── templates/                 # Global templates
└── legacygrid_school_management/
    └── settings.py            # Secure configuration
```

## 🛠️ Installation & Setup

### 1. Basic Setup
```bash
pip install django pillow stripe
python manage.py migrate
python manage.py createsuperuser --username Uncle-T36
python manage.py runserver
```

### 2. Environment Configuration
Create a `.env` file with your secure credentials:

```bash
# Stripe Configuration (Production)
STRIPE_SECRET_KEY=sk_live_your_actual_secret_key_here
STRIPE_PUBLIC_KEY=pk_live_your_actual_public_key_here
STRIPE_PRICE_ID=price_your_actual_price_id_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# OpenAI Integration
OPENAI_API_KEY=sk-your_actual_openai_key_here

# Domain Configuration
DOMAIN=https://your-production-domain.com

# Security Settings
DEMO_MODE=False  # Set to True for development
```

### 3. Security Configuration
- Ensure HTTPS is enabled in production
- Configure Stripe webhooks for payment confirmation
- Set up proper SSL certificates
- Enable rate limiting on payment endpoints

## 🔒 Access Control

### Billing Pages (Owner-Only)
- `/billing/dashboard/` - Billing overview and status
- `/billing/subscription/` - Subscription management
- `/billing/settings/` - Payment configuration
- `/billing/not-authorized/` - Access denied page

### Security Measures
- **Authentication Required**: All billing pages require login
- **Owner Verification**: Username must match `Uncle-T36`
- **Automatic Redirection**: Non-owners redirected to access denied page
- **Session Security**: Secure session management
- **CSRF Protection**: Built-in Django CSRF protection

## 📧 Email System

Automated email notifications for school events (payments, registrations, etc.), using customizable templates.

### Setup
1. Fill in your SMTP credentials in `smtp_config_example.py`.
2. Add/edit templates in the `templates/` directory.
3. Use `auto_emailer.py` to send emails for different events.

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

## 🛡️ Security Best Practices

### For Production Deployment
1. **Never expose secret keys** in frontend code or version control
2. **Use environment variables** for all sensitive configuration
3. **Enable webhook signatures** to verify payment authenticity
4. **Implement rate limiting** on payment endpoints
5. **Monitor for suspicious activity** and unauthorized access attempts
6. **Regular backups** of billing and user data
7. **Regular security audits** and penetration testing

### Monitoring & Alerts
- Transaction logging enabled
- Security alerts for unauthorized access attempts
- Daily backup status monitoring
- SSL certificate monitoring

## 📞 Support

- **Security Issues**: Report immediately to `support@legacygrid.co.zw`
- **Documentation**: [GitHub Repository](https://github.com/Uncle-T36/legacygrid-school-management)
- **Owner Access**: Restricted to `Uncle-T36` only

## 🧪 Testing

### Demo Mode
- Set `DEMO_MODE=True` in settings for safe testing
- No real payments processed in demo mode
- All Stripe operations use test keys
- Clear indicators throughout the UI

### Error Logging
All errors are logged in `email_error.log`.

## 🔄 Extending

- Add more templates to the `templates/` directory
- Map new events/templates in `TEMPLATE_MAP` in `auto_emailer.py`
- Billing features can only be extended by the system owner

---

**⚠️ IMPORTANT**: This system contains sensitive financial data and is protected by strict access controls. Only authorized personnel should have access to production credentials and billing information.