# LegacyGrid School Management System

A comprehensive school management system built with Django, specifically designed for Zimbabwean schools with advanced billing and subscription automation.

## 🌟 Features

### 🔐 Owner-Only Billing Dashboard
- **Exclusive Access**: Only Uncle-T36 (system owner) can access billing features
- **Complete Control**: Full billing, subscription, and payment management
- **Revenue Analytics**: Real-time revenue tracking and reporting
- **Subscription Management**: Monitor all user subscriptions and statuses

### 💰 Multi-Currency Support
- **Zimbabwe Focus**: Primary support for ZWL (Zimbabwean Dollar) and USD
- **Regional Support**: ZAR (South African Rand), NGN (Nigerian Naira), KES (Kenyan Shilling)
- **Auto-Conversion**: All payments automatically converted to USD for internal accounting
- **Real-Time Rates**: Exchange rates updated automatically from external APIs

### 🏦 Payment Provider Integration

#### 💳 International Cards
- **Stripe**: Credit/debit cards, Apple Pay, Google Pay
- **PayPal**: Global payment processing

#### 📱 Zimbabwe Mobile Money (Default Options)
- **EcoCash**: ZWL and USD support
- **OneMoney**: ZWL and USD support  
- **Telecash**: ZWL support
- **MTN Mobile Money**: Regional support
- **Airtel Money**: Cross-border payments

#### 💼 eWallets
- **Skrill**: Digital wallet payments
- **Neteller**: Online money transfers

### 🤖 Automated Subscription Management
- **Instant Activation**: Subscriptions activate automatically when payment is confirmed
- **Webhook Integration**: Real-time payment status updates from all providers
- **Offline Processing**: Works even when the owner is offline
- **Payment Retry Logic**: Automatic handling of failed payments

### 🌍 Zimbabwe Localization & Multi-Language
- **Multi-Language Profiles**: Users can set preferred language (English, Shona, Ndebele)
- **Message Templates**: SMS, email, and in-app notifications in user's preferred language
- **Mass Messaging**: Broadcast messages to multiple users in their preferred languages
- **Zimbabwe Timezone**: Configured for Africa/Harare timezone

### 🔧 Modular Architecture
- **Easy Integration**: Standard webhook endpoints for all providers
- **Plug-and-Play**: Add or remove payment providers easily
- **Consistent Data Models**: Unified approach to payment processing
- **Configuration Management**: Enable/disable providers and set regional defaults

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 5.2+
- Pillow (for image handling)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Uncle-T36/legacygrid-school-management.git
   cd legacygrid-school-management
   ```

2. **Install dependencies**
   ```bash
   pip install django pillow
   ```

3. **Set up the database**
   ```bash
   python manage.py migrate
   ```

4. **Create initial data**
   ```bash
   python manage.py setup_billing_data
   ```

5. **Create the owner superuser**
   ```bash
   python manage.py createsuperuser
   # Use username: Uncle-T36
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the billing dashboard**
   - Navigate to `http://localhost:8000/billing/`
   - Login as Uncle-T36 to access billing features

## 📊 Billing Dashboard

### Main Dashboard (`/billing/`)
- Revenue overview and analytics
- Active subscription count
- Pending payment monitoring
- Recent payment history
- Quick access to all billing features

### Currency Management (`/billing/currencies/`)
- Supported currency overview
- Exchange rate management
- Auto-update from external APIs
- Zimbabwe-specific currency highlighting

### Payment Providers (`/billing/providers/`)
- All integrated payment methods
- Provider status and configuration
- Supported currencies per provider
- Zimbabwe default payment methods

### Subscription Management (`/billing/subscriptions/`)
- All user subscriptions
- Status tracking and management
- Subscription actions (activate, suspend, cancel)
- Search and filtering options

### Payment Management (`/billing/payments/`)
- Complete payment history
- Payment status tracking
- Provider-specific filtering
- Transaction details and references

### Message Templates (`/billing/templates/`)
- Multi-language notification templates
- SMS, email, and in-app message management
- Event-based messaging (payment success, failure, etc.)
- Mass messaging capabilities

## 🔗 Webhook Endpoints

The system provides secure webhook endpoints for real-time payment processing:

- **Stripe**: `/billing/webhooks/stripe/`
- **PayPal**: `/billing/webhooks/paypal/`
- **Mobile Money**: `/billing/webhooks/mobile-money/?provider=[provider_type]`

All webhooks validate payment authenticity and process payments automatically.

## 💡 Architecture

### Models
- **Currency**: Supported currencies and exchange rates
- **SubscriptionPlan**: Available subscription tiers
- **PaymentProvider**: Integrated payment methods
- **UserProfile**: Extended user profiles with language preferences
- **Subscription**: User subscription records
- **Payment**: Payment transaction history
- **WebhookEvent**: Webhook event logging
- **MessageTemplate**: Multi-language message templates
- **NotificationLog**: Sent notification tracking

### Services
- **CurrencyService**: Exchange rate management and conversion
- **PaymentService**: Payment processing and webhook handling
- **NotificationService**: Multi-language messaging system

### Security
- **Owner-Only Access**: All billing features restricted to Uncle-T36
- **Webhook Validation**: Secure payment confirmation
- **Permission Decorators**: Comprehensive access control
- **CSRF Protection**: Standard Django security features

## 🇿🇼 Zimbabwe-Specific Features

### Default Payment Methods
- EcoCash, OneMoney, and Telecash are marked as Zimbabwe defaults
- Mobile money providers support both ZWL and USD
- Prioritized in payment selection for Zimbabwean users

### Local Currency Support
- Zimbabwean Dollar (ZWL) with real-time exchange rates
- USD support for dual-currency economy
- Automatic conversion for accounting purposes

### Multi-Language Support
- **English**: Default language
- **Shona**: Native Zimbabwean language
- **Ndebele**: Native Zimbabwean language
- User-selectable language preferences
- Localized payment notifications

### Regional Integration
- Africa/Harare timezone configuration
- Mobile money integration for regional providers
- Cross-border payment support with neighboring countries

## 🔧 Configuration

### Payment Provider Setup
1. Access the admin interface (`/admin/`)
2. Navigate to Billing > Payment Providers
3. Configure API keys and settings for each provider
4. Set supported currencies and regional defaults

### Currency Management
1. Access Currency Management (`/billing/currencies/`)
2. Update exchange rates (automatic or manual)
3. Add new currencies as needed
4. Configure regional preferences

### Message Templates
1. Access Message Templates (`/billing/templates/`)
2. Create templates for each language and channel
3. Use template variables for dynamic content
4. Test message delivery

## 📈 Analytics and Reporting

### Revenue Tracking
- Real-time revenue analytics
- Multi-currency revenue conversion
- Monthly and yearly reporting
- Payment provider performance

### Subscription Analytics
- Active subscription monitoring
- Churn rate tracking
- Plan popularity analysis
- Geographic distribution

### Payment Analytics
- Success/failure rates by provider
- Currency preference analysis
- Peak payment time analysis
- Regional payment method preferences

## 🔒 Security and Compliance

### Data Protection
- User payment data encryption
- Secure webhook validation
- PCI DSS compliance (through providers)
- GDPR-compliant data handling

### Access Control
- Owner-only billing access
- Permission-based feature restrictions
- Audit logging for all actions
- Secure admin interface

## 📞 Support and Documentation

### Owner Support
- Full system documentation
- Payment provider integration guides
- Troubleshooting documentation
- Performance optimization tips

### Multi-Language Help
- Documentation available in English, Shona, and Ndebele
- Context-sensitive help system
- Video tutorials for common tasks
- Community support forum

## 🚀 Deployment

### Production Setup
1. Configure production database (PostgreSQL recommended)
2. Set up payment provider webhooks
3. Configure email/SMS services
4. Set up SSL certificates
5. Configure environment variables
6. Set `DEBUG = False` in production

### Environment Variables
```bash
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
STRIPE_SECRET_KEY=your-stripe-key
PAYPAL_CLIENT_ID=your-paypal-id
EXCHANGE_RATE_API_KEY=your-api-key
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📮 Contact

For questions or support, contact Uncle-T36 or open an issue on GitHub.

---

**Built with ❤️ for Zimbabwean schools**