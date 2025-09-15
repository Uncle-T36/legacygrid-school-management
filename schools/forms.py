from django import forms
from .models import School

class SchoolLogoForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'logo', 'address']
