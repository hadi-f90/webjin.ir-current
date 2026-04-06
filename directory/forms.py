from django import forms
from .models import Website, Category
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class WebsiteSubmitForm(forms.ModelForm):
    """Form for users to submit new websites"""
    # Optional custom slug field
    custom_slug = forms.SlugField(
        required=False,
        label='اسلاگ سفارشی (اختیاری)',
        help_text='آدرس اختصاصی برای وب‌سایت شما (اختیاری)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'my-website'
        })
    )

    class Meta:
        model = Website
        fields = ['title', 'custom_slug','url', 'description', 'category', 'owner_name', 'owner_email']
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

    def clean_url(self):
        url = self.cleaned_data.get('url', '').strip()

        if not url:
            raise ValidationError("آدرس وب‌سایت الزامی است.")

        # Add https:// if no protocol exists
        if not url.startswith(('http://', 'https://', 'www')):
            url = 'https://' + url

        # Validate the URL
        try:
            validator = URLValidator(schemes=['http', 'https'])
            validator(url)
        except ValidationError:
            raise ValidationError("آدرس وب‌سایت معتبر نیست.")

        return url

    def clean_custom_slug(self):
        slug = self.cleaned_data.get('custom_slug', '').strip()

        if slug:
            # Check if slug already exists
            from django.utils.text import slugify

            slug = slugify(slug)

            if Website.objects.filter(slug=slug).exists():
                raise ValidationError("این اسلاگ قبلاً استفاده شده است.")

        return slug

    def save(self, commit=True):
        website = super().save(commit=False)

        # Use custom slug if provided, otherwise will be auto-generated in model save()
        if self.cleaned_data.get('custom_slug'):
            from django.utils.text import slugify

            website.slug = slugify(self.cleaned_data['custom_slug'])

        if commit:
            website.save()

        return website


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