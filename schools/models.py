from django.db import models
from django.conf import settings
from core.models import Tenant

class School(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_schools")
    address = models.CharField(max_length=255, blank=True)
    
    # Multi-tenant support
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="schools")
    
    # Additional school information for international use
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Academic settings
    academic_year_start = models.DateField(null=True, blank=True)
    academic_year_end = models.DateField(null=True, blank=True)
    
    # Localization
    timezone = models.CharField(max_length=50, default='UTC')
    preferred_language = models.CharField(max_length=10, default='en')
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
