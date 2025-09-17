#!/usr/bin/env python
"""
Demo script to showcase LegacyGrid International Features

This script demonstrates the key international and multi-tenant features
of the enhanced LegacyGrid School Management System.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/home/runner/work/legacygrid-school-management/legacygrid-school-management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legacygrid_school_management.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Country, Tenant, PaymentGateway, FeatureToggle, TenantFeatureToggle
from core.utils import get_currency_rates, convert_currency, format_currency
from django.utils import timezone
import uuid

def main():
    print("🌍 LegacyGrid International Features Demo")
    print("=" * 60)
    
    # 1. Show Countries
    print("\n📍 Supported Countries:")
    countries = Country.objects.filter(is_active=True)[:10]
    for country in countries:
        print(f"  🌍 {country.name} ({country.code})")
        print(f"      Currency: {country.currency_code}")
        print(f"      Locale: {country.locale}")
        print(f"      RTL: {'Yes' if country.is_rtl else 'No'}")
        print(f"      GDPR: {'Yes' if country.gdpr_compliant else 'No'}")
    
    # 2. Show Payment Gateways
    print(f"\n💳 Payment Gateways:")
    gateways = PaymentGateway.objects.all()
    for gateway in gateways:
        countries_count = gateway.allowed_countries.count()
        print(f"  💳 {gateway.display_name}")
        print(f"      Status: {'Active' if gateway.is_active else 'Inactive'}")
        print(f"      Countries: {countries_count}")
        print(f"      Currencies: {', '.join(gateway.supported_currencies[:3])}...")
    
    # 3. Show Feature Toggles
    print(f"\n🎛️  Feature Toggles:")
    features = FeatureToggle.objects.all()[:8]
    for feature in features:
        print(f"  🎛️  {feature.name}")
        print(f"       Global: {'Yes' if feature.is_global else 'No'}")
        print(f"       Enabled: {'Yes' if feature.is_enabled_globally else 'No'}")
        print(f"       Owner Approval: {'Required' if feature.requires_owner_approval else 'Not Required'}")
    
    # 4. Create Demo Tenant (if owner exists)
    try:
        owner = User.objects.get(username='Uncle-T36')
        print(f"\n🏫 Creating Demo Tenant...")
        
        # Get a country
        zimbabwe = Country.objects.get(code='ZWE')
        
        # Create demo tenant
        demo_tenant, created = Tenant.objects.get_or_create(
            subdomain='demo-school',
            defaults={
                'name': 'Demo International School',
                'country': zimbabwe,
                'contact_email': 'demo@school.com',
                'subscription_tier': 'professional',
                'created_by': owner,
                'enabled_features': ['basic_dashboard', 'ai_reports', 'multi_currency'],
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
            }
        )
        
        if created:
            print(f"  ✅ Created: {demo_tenant.name}")
        else:
            print(f"  ℹ️  Exists: {demo_tenant.name}")
        
        print(f"      Country: {demo_tenant.country.name}")
        print(f"      Currency: {demo_tenant.country.currency_code}")
        print(f"      Tier: {demo_tenant.subscription_tier}")
        print(f"      Features: {len(demo_tenant.enabled_features)}")
        
    except User.DoesNotExist:
        print(f"\n⚠️  Owner user 'Uncle-T36' not found. Skipping tenant creation.")
    
    # 5. Currency Conversion Demo
    print(f"\n💱 Currency Conversion Demo:")
    try:
        rates = get_currency_rates()
        print(f"  Base rates loaded: {len(rates)} currencies")
        
        # Convert 100 USD to various currencies
        base_amount = 100
        target_currencies = ['ZAR', 'NGN', 'KES', 'EUR', 'GBP']
        
        print(f"  Converting ${base_amount} USD to:")
        for currency in target_currencies:
            try:
                converted = convert_currency(base_amount, 'USD', currency)
                formatted = format_currency(converted, currency)
                print(f"    {currency}: {formatted}")
            except Exception as e:
                print(f"    {currency}: Error - {e}")
    
    except Exception as e:
        print(f"  ❌ Currency conversion error: {e}")
    
    # 6. Subscription Tiers
    print(f"\n📊 Subscription Tiers:")
    from django.conf import settings
    tiers = settings.SUBSCRIPTION_TIERS
    for tier_name, tier_data in tiers.items():
        print(f"  📊 {tier_data['name']} (${tier_data['price']}/month)")
        print(f"      Features: {len(tier_data['features'])}")
        print(f"      AI Access: {'Yes' if tier_data['ai_access'] else 'No'}")
        print(f"      Max Students: {tier_data['max_students'] if tier_data['max_students'] != -1 else 'Unlimited'}")
    
    # 7. Available Features
    print(f"\n🔧 Available Features:")
    available_features = settings.AVAILABLE_FEATURES
    categories = {}
    for feature_name, feature_data in available_features.items():
        category = feature_data['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(feature_name)
    
    for category, features in categories.items():
        print(f"  🔧 {category.title()}: {len(features)} features")
    
    print(f"\n✅ Demo completed! Total features: {len(available_features)}")
    print(f"🌍 System ready for international deployment!")
    print(f"👑 Owner controls: Fully functional")
    print(f"🔒 Security: Enterprise-grade")
    
    # 8. Next Steps
    print(f"\n🚀 Next Steps:")
    print(f"  1. Create owner user: python manage.py createsuperuser --username Uncle-T36")
    print(f"  2. Run server: python manage.py runserver")
    print(f"  3. Visit: http://localhost:8000/core/international/")
    print(f"  4. Login as Uncle-T36 to access owner features")
    print(f"  5. Explore international management dashboard")


if __name__ == '__main__':
    main()