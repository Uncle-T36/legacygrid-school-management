from django import forms
from .models import School

class SchoolForm(forms.ModelForm):
    """Form for creating and editing schools"""
    class Meta:
        model = School
        fields = ['name', 'logo', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter school name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter school address'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class SchoolLogoForm(forms.ModelForm):
    """Form for updating school profile and logo"""
    class Meta:
        model = School
        fields = ['name', 'logo', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
