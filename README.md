# LegacyGrid School Management System

A comprehensive Django-based school management system with secure billing, subscription management, and user authentication.

## 🚀 Features

### Authentication & User Management
- **User Registration**: New users can create accounts
- **Login/Logout**: Secure authentication system
- **Session Management**: Protected user sessions
- **Role-based Access**: Different access levels for users and owners

### School Management
- **School Profiles**: Create and manage school information
- **Logo Upload**: Upload and display school logos
- **School Directory**: Browse all schools in the system
- **Owner Controls**: Users can only edit schools they own
- **Profile Management**: Comprehensive school profile editing

### Secure Billing System
- **Owner-Only Access**: Billing restricted to system owner (`Uncle-T36`)
- **Stripe Integration**: Secure payment processing
- **Subscription Management**: Handle different subscription tiers
- **Demo Mode**: Safe testing environment
- **Access Control**: Automatic redirection for unauthorized users

### User Interface
- **Responsive Design**: Mobile-friendly navigation
- **Template Inheritance**: Consistent styling across pages
- **Navigation Bar**: Easy access to all features
- **Flash Messages**: User feedback for actions
- **Modern Styling**: Clean, professional appearance

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Django 5.2+
- Pillow (for image handling)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Uncle-T36/legacygrid-school-management.git
   cd legacygrid-school-management
   ```

2. **Install dependencies**
   ```bash
   pip install django pillow
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser** (optional)
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   Open your browser to `http://localhost:8000`

### First Steps
1. Register a new account or login
2. Create your school profile
3. Upload a school logo
4. Browse other schools in the directory
5. (Owner only) Access billing features

## 📁 Project Structure

```
legacygrid_school_management/
├── billing/                    # Owner-only billing app
│   ├── views.py               # Billing views with @owner_only decorator
│   ├── urls.py                # Billing URL routing
│   └── templates/billing/     # Secure billing templates
├── schools/                   # School management app
│   ├── views.py              # School and auth views
│   ├── auth_views.py         # Authentication views
│   ├── models.py             # School model
│   ├── forms.py              # School forms
│   ├── tests.py              # Comprehensive test suite
│   └── templates/            # School templates
├── templates/                 # Global templates
│   ├── base.html             # Main base template with navigation
│   └── registration/         # Authentication templates
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User uploads (school logos)
└── legacygrid_school_management/
    ├── settings.py           # Django configuration
    └── urls.py              # Main URL routing
```

## 🔒 Access Control & Security

### Authentication Views
- `/login/` - User login
- `/logout/` - User logout  
- `/register/` - New user registration

### School Management (Authenticated Users)
- `/` - Homepage with feature overview
- `/schools/list/` - Browse all schools
- `/schools/create/` - Create new school
- `/schools/profile/` - Manage your school profile
- `/schools/edit/<id>/` - Edit school (owners only)

### Billing Pages (Owner-Only)
- `/billing/dashboard/` - Billing overview and status
- `/billing/subscription/` - Subscription management
- `/billing/settings/` - Payment configuration
- `/billing/not-authorized/` - Access denied page

### Security Measures
- **Authentication Required**: All management features require login
- **Owner Verification**: Billing access restricted to `Uncle-T36`
- **Automatic Redirection**: Non-owners redirected to access denied page
- **Session Security**: Secure session management
- **CSRF Protection**: Built-in Django CSRF protection
- **Input Validation**: Form validation and sanitization

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test schools
python manage.py test billing

# Run with verbose output
python manage.py test --verbosity=2
```

### Test Coverage
- **Homepage Tests**: Status codes, templates, content
- **Authentication Tests**: Login, logout, registration
- **School Profile Tests**: Profile management, permissions
- **School List Tests**: Directory browsing, authentication
- **Form Tests**: Validation and error handling

### Demo Mode
- Set `DEMO_MODE=True` in settings for safe testing
- No real payments processed in demo mode
- All Stripe operations use test keys
- Clear indicators throughout the UI

## 📧 Email System

Automated email notifications for school events (payments, registrations, etc.), using customizable templates.

### Setup
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

## 🔄 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `python manage.py test`
6. Commit changes: `git commit -m "Add feature description"`
7. Push to your fork: `git push origin feature-name`
8. Create a Pull Request

### Coding Standards
- Follow Django best practices
- Write tests for new features
- Use meaningful commit messages
- Add docstrings to functions and classes
- Follow PEP 8 Python style guide

### Areas for Contribution
- Additional school management features
- Enhanced user profile management
- Email template improvements
- UI/UX enhancements
- Documentation improvements
- Test coverage expansion

## 💳 Billing & Payments

### Payment Integration
- **Stripe Integration**: Secure payment processing
- **Test Mode**: Safe development environment
- **Webhook Support**: Real-time payment updates
- **Multiple Currencies**: Support for various currencies
- **Subscription Tiers**: Free and premium plans

### Configuration
Update `settings.py` with your payment credentials:
```python
STRIPE_SECRET_KEY = 'your_stripe_secret_key'
STRIPE_PUBLIC_KEY = 'your_stripe_public_key'
STRIPE_PRICE_ID = 'your_price_id'
```

## 🛡️ Security Best Practices

- **Environment Variables**: Store sensitive data in environment variables
- **Owner-Only Billing**: Billing features restricted to system owner
- **Input Validation**: All user input is validated and sanitized
- **HTTPS Required**: Use HTTPS in production
- **Regular Updates**: Keep dependencies up to date
- **Access Logging**: Monitor and log access attempts

## 📞 Support

- **Documentation**: Check this README for setup and usage
- **Issues**: Report bugs via GitHub Issues
- **Email**: Contact support@legacygrid.co.zw
- **Owner Access**: Only Uncle-T36 can modify billing settings

## 🏷️ Version & License

- **Version**: 1.0.0
- **Django Version**: 5.2+
- **Python Version**: 3.8+
- **License**: Custom - Contact owner for licensing terms

---

**⚠️ IMPORTANT**: This system contains sensitive financial data and is protected by strict access controls. Only authorized personnel should have access to production credentials and billing information.

**🔐 Owner Access**: Billing and subscription management is restricted to the verified owner account (Uncle-T36) for security purposes.

For questions about accessing billing features or system ownership, please contact the system administrator.
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