# LegacyGrid School Management System

**OWNER-ONLY LICENSE**

This project is protected by a custom OWNER-ONLY LICENSE. Only the original owner (Uncle-T36) is permitted to use this code for commercial, production, or monetized purposes. All other use is strictly limited to non-commercial, educational, or personal experimentation.

**Absolutely no cloning, redistribution, resale, or monetization is permitted. Violators will be subject to legal action under the laws of Zimbabwe.**

See the [LICENSE](LICENSE) file for details.

---

A comprehensive Django-based school management system with secure billing and subscription management.

## 🔐 Security Features

This system implements **configurable owner-only access controls** for all billing and subscription management:

- **Configurable Owner Access**: Owner username is configurable via environment variables for easy transfer
- **Secure API Key Management**: All sensitive keys stored as environment variables
- **Payment Security**: Multiple payment gateway support with test/live mode configuration
- **Access Control**: Custom decorators ensure unauthorized users are blocked
- **Audit Logging**: All access attempts are monitored and logged
- **Production Ready**: Environment-driven configuration for secure deployment

## 🏗️ System Architecture

### Core Applications
- **Schools**: School profile and management
- **Billing**: Secure payment and subscription management (Owner-configurable)
- **Account**: User profile and account management

### Security Implementation
- Custom `@owner_only` decorator with configurable owner username
- Automatic redirection to "Not Authorized" page for non-owners
- Environment variable protection for all sensitive credentials
- Multiple payment gateway support (Stripe, PayPal, EcoCash, OneMoney)

## 💳 Billing & Payments

### Configurable Owner Access
The system owner (configurable via `OWNER_USERNAME` environment variable) can:
- View billing dashboard
- Manage subscriptions
- Configure payment settings
- Access financial data

### Multi-Gateway Payment Support
- **Stripe**: Full integration with test/live modes
- **PayPal**: Sandbox/live configuration support  
- **EcoCash**: Zimbabwe mobile money integration
- **OneMoney**: Zimbabwe mobile money integration
- **Secure Keys**: All gateway credentials via environment variables
- **Webhook Support**: Payment confirmation and validation
- **Multiple Currencies**: USD, ZWL, ZAR, NGN, GBP, EUR

### Subscription Tiers
- **Free**: Basic dashboard and messaging
- **Premium**: Full features including AI access

## 📁 Project Structure

```
legacygrid_school_management/
├── account/                     # User account management
│   ├── views.py                # Profile and account views
│   ├── urls.py                 # Account URL routing
│   └── templates/account/      # Account management templates
├── billing/                    # Owner-configurable billing app
│   ├── views.py               # Billing views with @owner_only decorator
│   ├── urls.py                # Billing URL routing
│   └── templates/billing/     # Secure billing templates
├── schools/                   # School management
├── templates/                 # Global templates
├── .env.example              # Environment variables template
└── legacygrid_school_management/
    └── settings.py           # Environment-driven configuration
```

## 🛠️ Installation & Setup

### 1. Basic Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Or install manually:
pip install django pillow stripe python-dotenv

# Run migrations
python manage.py migrate

# Create superuser (use your desired owner username)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and configure your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your actual values:

```bash
# Django Configuration
SECRET_KEY=your-secure-django-secret-key-here
DEBUG=False  # Set to False for production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Owner Configuration (IMPORTANT for ownership transfer)
OWNER_USERNAME=your-owner-username-here
ALLOW_ONLY_OWNER_BILLING=True

# Domain Configuration
DOMAIN=https://your-production-domain.com

# Demo Mode and Security
DEMO_MODE=False  # Set to False for production
AI_FEATURES_REQUIRE_PAYMENT=True
PREMIUM_FEATURES_REQUIRE_PAYMENT=True

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_actual_secret_key_here
STRIPE_PUBLIC_KEY=pk_live_your_actual_public_key_here
STRIPE_PRICE_ID=price_your_actual_price_id_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# OpenAI Integration
OPENAI_API_KEY=sk-your_actual_openai_key_here

# PayPal Configuration
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=live  # or 'sandbox' for testing

# Zimbabwe Mobile Money (Optional)
ECOCASH_MERCHANT_CODE=your_ecocash_merchant_code
ECOCASH_API_URL=https://api.ecocash.co.zw/
ECOCASH_MODE=live

ONEMONEY_MERCHANT_CODE=your_onemoney_merchant_code
ONEMONEY_API_URL=https://onemoney.co.zw/api/
ONEMONEY_MODE=live

# Support and Documentation
SUPPORT_EMAIL=support@yourcompany.com
```

### 3. Security Configuration
- Ensure HTTPS is enabled in production
- Configure webhooks for payment gateways
- Set up proper SSL certificates
- Enable rate limiting on payment endpoints
- Configure firewall and security groups
- Set up monitoring and logging

## 🔄 Owner Transfer & SaaS Setup

### For New Owners/SaaS Deployment

This system is designed for easy ownership transfer. To transfer ownership or deploy as SaaS:

#### 1. Update Owner Configuration
```bash
# In your .env file
OWNER_USERNAME=new-owner-username
ALLOW_ONLY_OWNER_BILLING=True

# For SaaS with multiple admins:
ALLOW_ONLY_OWNER_BILLING=False
```

#### 2. Create New Owner User
```bash
# Create new superuser with desired username
python manage.py createsuperuser --username new-owner-username

# Or update existing user in Django admin
# Set is_staff=True and is_superuser=True for admin access
```

#### 3. Update Payment Gateway Accounts
- Transfer Stripe account or create new one
- Update PayPal business account details
- Configure mobile money merchant accounts
- Update OpenAI API account

#### 4. Update Branding and Contact Information
```bash
# In .env file
SUPPORT_EMAIL=new-owner@newcompany.com
DOMAIN=https://new-domain.com
```

#### 5. For SaaS Multi-Tenancy
To convert to SaaS with multiple paying customers:
```bash
# Disable owner-only restrictions
ALLOW_ONLY_OWNER_BILLING=False
PREMIUM_FEATURES_REQUIRE_PAYMENT=True
AI_FEATURES_REQUIRE_PAYMENT=True
```

## ✅ Production Deployment Checklist

### Security
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Generate new `SECRET_KEY` for production
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure secure headers and middleware
- [ ] Set up firewall rules
- [ ] Enable Django security middleware
- [ ] Configure CSRF and session security

### Environment Variables
- [ ] Copy `.env.example` to `.env`
- [ ] Set all required environment variables
- [ ] Use production API keys (not test keys)
- [ ] Set `DEMO_MODE=False`
- [ ] Configure production database settings
- [ ] Set up email backend for production
- [ ] Configure logging settings

### Payment Gateways
- [ ] Switch Stripe to live mode with live keys
- [ ] Configure production Stripe webhooks
- [ ] Set up PayPal production account
- [ ] Configure mobile money production endpoints
- [ ] Test all payment flows
- [ ] Set up payment monitoring and alerts
- [ ] Configure refund and dispute handling

### Database & Storage
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure database backups
- [ ] Set up static file serving (CDN/S3)
- [ ] Configure media file storage
- [ ] Set up database connection pooling
- [ ] Configure database monitoring

### Monitoring & Logging
- [ ] Set up application monitoring (Sentry, etc.)
- [ ] Configure error logging and alerts
- [ ] Set up performance monitoring
- [ ] Configure uptime monitoring
- [ ] Set up log aggregation
- [ ] Configure backup monitoring

### Infrastructure
- [ ] Set up load balancing (if needed)
- [ ] Configure auto-scaling
- [ ] Set up CI/CD pipeline
- [ ] Configure staging environment
- [ ] Set up health checks
- [ ] Configure disaster recovery plan

### Testing
- [ ] Run all tests in production environment
- [ ] Test payment flows with small amounts
- [ ] Verify email delivery works
- [ ] Test all user flows and permissions
- [ ] Perform security testing
- [ ] Load test critical endpoints

## 🔒 Access Control

### Billing Pages (Owner-Configurable)
- `/billing/dashboard/` - Billing overview and status
- `/billing/subscription/` - Subscription management
- `/billing/settings/` - Payment configuration
- `/billing/not-authorized/` - Access denied page

### Security Measures
- **Authentication Required**: All billing pages require login
- **Owner Verification**: Username configurable via `OWNER_USERNAME` environment variable
- **Automatic Redirection**: Non-owners redirected to access denied page
- **Session Security**: Secure session management
- **CSRF Protection**: Built-in Django CSRF protection
- **Environment-Driven**: All security settings configurable via environment variables

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

- **Security Issues**: Report immediately to the configured support email (see `SUPPORT_EMAIL` in .env)
- **Documentation**: [GitHub Repository](https://github.com/Uncle-T36/legacygrid-school-management)
- **Owner Access**: Configurable via `OWNER_USERNAME` environment variable

## 🧪 Testing

### Demo Mode
- Set `DEMO_MODE=True` in .env for safe testing
- No real payments processed in demo mode
- All payment gateways use test/sandbox keys
- Clear indicators throughout the UI

### Error Logging
All errors are logged in `email_error.log`.

## 🔄 Extending

- Add more templates to the `templates/` directory
- Map new events/templates in `TEMPLATE_MAP` in `auto_emailer.py`
- Billing features can be extended by the configured system owner
- Payment gateways can be added to the `PAYMENT_GATEWAYS` configuration

## 💡 Key Features for Production

### Environment-Driven Configuration
- All secrets and configuration via environment variables
- Easy deployment across different environments
- Secure credential management
- Configurable for different deployment scenarios

### Multi-Gateway Payment Support
- Stripe for international payments
- PayPal for alternative payment methods
- EcoCash and OneMoney for Zimbabwe market
- Easy to add additional payment gateways

### Flexible Ownership Model
- Configurable owner username for easy transfer
- SaaS-ready with configurable access controls
- Environment-driven security settings
- Easy white-labeling and rebranding

---

**⚠️ IMPORTANT**: This system handles sensitive financial data. Always use environment variables for secrets, enable HTTPS in production, and follow the production checklist before deploying. For ownership transfer, simply update the `.env` file with new credentials and owner information.