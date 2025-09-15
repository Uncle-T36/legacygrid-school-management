from django.db import models
from django.conf import settings

class School(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_schools")
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
