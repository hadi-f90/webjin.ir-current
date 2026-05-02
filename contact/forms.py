from django import forms
from .models import Contact
from captcha.fields import CaptchaField


class ContactForm(forms.ModelForm):
    """Contact form."""

    captcha = CaptchaField()

    class Meta:
        """fields to be used by form."""

        model = Contact
        exclude = ('datetime_created', 'spam_status', )
        labels = {
            'captcha': 'تشخیص ربات',
        }
        
        help_text = {
            'captcha': 'انسان یا ربات؟'
        }
