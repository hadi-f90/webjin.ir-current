from django import forms
from .models import Website, Category

class WebsiteSubmitForm(forms.ModelForm):
    """Form for users to submit new websites"""
    class Meta:
        model = Website
        fields = ['title', 'url', 'description', 'category', 'owner_name', 'owner_email']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Website Title'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your website...'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'owner_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
        }


class WebsiteAdminForm(forms.ModelForm):
    """Form for admin to edit website with all fields"""
    class Meta:
        model = Website
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'vTextField'}),
            'url': forms.URLInput(attrs={'class': 'vTextField'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }