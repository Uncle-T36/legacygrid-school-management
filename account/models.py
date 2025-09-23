from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class UserProfile(models.Model):
    """Extended user profile with additional fields for user customization"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text='Tell us about yourself')
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        help_text='Profile picture'
    )
    language_preference = models.CharField(
        max_length=2,
        choices=settings.LANGUAGES,
        default='en',
        help_text='Preferred language for the interface'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
