# LegacyGrid School Management

A Django-based school management system with integrated billing and subscription management powered by Stripe.

## Features

- School profile management
- Secure billing and subscription management (Owner-only access)
- Stripe payment integration (Test mode)
- User authentication and authorization

## Billing & Subscription Access Control

**Important: Only the project owner can access billing and subscription management.**

### Owner Access Restrictions

The billing and subscription management features are restricted to the project owner only:
- **Owner Username**: `Uncle-T36`
- **Restricted Areas**:
  - `/billing/` - Billing dashboard
  - `/billing/subscription/` - Subscription management
  - `/billing/settings/` - Billing settings

### Access Control Implementation

1. **Authentication Required**: Users must be logged in to attempt access
2. **Owner Verification**: System checks if `request.user.username == 'Uncle-T36'`
3. **Access Denied**: Non-owners are redirected to a "Not Authorized" page with clear messaging

### Changing Owner Access

To change who can access billing and subscription management:

1. Open `billing/views.py`
2. Locate the `owner_required` decorator function
3. Update the username check:
   ```python
   if request.user.username != 'YOUR_NEW_OWNER_USERNAME':
   ```
4. Save the file and restart the application

**Security Note**: Only make this change if you need to transfer ownership. The restriction exists to protect sensitive billing information.

## Stripe Configuration

The application includes Stripe integration with the following placeholder settings in `settings.py`:

```python
# Stripe Configuration (Test Mode)
STRIPE_SECRET_KEY = 'sk_test_placeholder_key_replace_with_actual_test_key'
STRIPE_PUBLIC_KEY = 'pk_test_placeholder_key_replace_with_actual_test_key'
STRIPE_PRICE_ID = 'price_placeholder_replace_with_actual_price_id'
DOMAIN = 'http://localhost:8000'
```

### Setting Up Stripe (Test Mode)

1. Create a Stripe account at https://stripe.com
2. Navigate to Dashboard → Developers → API keys
3. Copy your test mode keys
4. Replace the placeholder values in `settings.py`
5. Create a product and price in Stripe Dashboard
6. Update `STRIPE_PRICE_ID` with your actual price ID

## Installation & Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install django pillow
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Security Features

- **Environment-based configuration**: Sensitive settings should use environment variables in production
- **Owner-only billing access**: Prevents unauthorized access to payment information
- **Test mode configuration**: Safe development environment setup
- **Clear access denial messaging**: Users understand why access is restricted

## Contributing

This project maintains strict access controls for billing functionality. When contributing:
- Respect the owner-only access pattern for billing features
- Never expose sensitive Stripe keys in code
- Use environment variables for production configurations
- Test access control restrictions thoroughly

## Support

For questions about billing access or configuration, contact the project owner (Uncle-T36).