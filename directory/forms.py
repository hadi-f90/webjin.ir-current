# directory/forms.py
from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from taggit.models import Tag  # Import from taggit, not local
from captcha.fields import CaptchaField  # <--- 1. Import this
from django.utils.text import slugify
import uuid
from .models import Website


class WebsiteSubmitForm(forms.ModelForm):
    """
    Form for submitting new websites.
    - Required fields: title, url, owner_name, owner_email, captcha
    - Optional fields: custom_slug, category, description, tags
    """

    # Custom slug field (optional)
    custom_slug = forms.SlugField(
        required=False,
        label="اسلاگ سفارشی",
        help_text="برای URL شخصی‌سازی شده (اختیاری)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'my-website'}),
    )

    # Tags input (handled via JavaScript)
    tags_input = forms.CharField(
        required=False, label="برچسب‌ها", widget=forms.HiddenInput(attrs={"id": "tagsInput"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make optional fields truly optional
        self.fields['description'].required = False
        self.fields['category'].required = False
        self.fields['custom_slug'].required = False

        # Add placeholder for category (empty option)

        category_choices = [('', "انتخاب کنید...")] + [
            (cat.pk, cat.name) for cat in self.fields['category'].queryset
        ]

        self.fields['category'].widget.choices = category_choices

    def clean_url(self):
        """Validate and normalize URL."""
        url = self.cleaned_data.get('url', '').strip()

        if not url:
            raise ValidationError("آدرس وب‌سایت الزامی است.")

        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Validate URL
        try:
            validator = URLValidator(schemes=['http', 'https'])
            validator(url)
        except ValidationError:
            raise ValidationError("آدرس وب‌سایت معتبر نیست.")

        return url

    def clean_custom_slug(self):
        """Validate and normalize custom slug."""
        slug = self.cleaned_data.get('custom_slug', '').strip()

        if not slug:
            return ''

        # Slugify the custom slug
        slug = slugify(slug)

        # Check for uniqueness
        if (
            Website.objects.exclude(pk=self.instance.pk if self.instance else None)
            .filter(slug=slug)
            .exists()
        ):
            # Generate unique slug by appending random suffix

            slug = f"{slug}-{uuid.uuid4().hex[:8]}"

        return slug

    def clean_description(self):
        """Clean description - make it optional."""
        description = self.cleaned_data.get('description', '').strip()
        return description if description else ''

    def clean_owner_name(self):
        """Validate owner name."""
        name = self.cleaned_data.get('owner_name', '').strip()
        if not name:
            raise ValidationError("نام شما الزامی است.")
        return name

    def clean_owner_email(self):
        """Validate owner email."""
        email = self.cleaned_data.get('owner_email', '').strip()
        if not email:
            raise ValidationError("ایمیل شما الزامی است.")
        return email

    def save(self, commit=True):
        """Save the website instance."""
        website = super().save(commit=False)

        # Handle custom slug
        custom_slug = self.cleaned_data.get('custom_slug', '')
        if custom_slug:
            website.slug = custom_slug
        else:
            # Auto-generate slug from title
            website.slug = slugify(self.cleaned_data.get('title', ''))

            # Ensure uniqueness
            base_slug = website.slug
            counter = 1
            while Website.objects.exclude(pk=website.pk).filter(slug=website.slug).exists():
                website.slug = f"{base_slug}-{counter}"
                counter += 1

        if commit:
            website.save()

        return website

def tag_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 1:
        return JsonResponse({'tags': []})

    tags = Tag.objects.filter(name__icontains=query)[:10]
    return JsonResponse({'tags': [{'id': t.id, 'name': t.name, 'slug': t.slug} for t in tags]})

class RatingForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, '⭐' * i) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'rating-star'}),
        label='امتیاز شما'
    )

class ReviewForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'نظر خود را بنویسید...'}),
        label='نظر شما'
    )

class ReportForm(forms.Form):
    REPORT_CHOICES = [
        ('broken', 'لینک خراب'),
        ('shutdown', 'وب‌سایت غیرفعال'),
        ('inappropriate', 'محتوای نامناسب'),
        ('scam', 'کلاهبرداری/فیشینگ'),
        ('other', 'دیگر'),
    ]
    report_type = forms.ChoiceField(
        choices=REPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='نوع گزارش'
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'توضیحات بیشتر'}),
        required=False,
        label='توضیحات'
    )

class QuickSubmitForm(forms.ModelForm):
    """
    فرم ساده برای کاربران مهمان جهت ثبت سریع وب‌سایت
    """
    title = forms.CharField(
        max_length=200,
        label='عنوان وب‌سایت',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: فروشگاه آنلاین دیجی‌کالا'
        })
    )
    url = forms.CharField(
        label='آدرس وب‌سایت',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'example.com'
        })
    )

    # <--- 1. Add CaptchaField here
    # We customize the widget to ensure it has the right classes for Bootstrap
    captcha = CaptchaField(
        label='کد امنیتی',
    )

    def clean_url(self):
        url = self.cleaned_data.get('url', '').strip()
        if not url:
            raise ValidationError('آدرس وب‌سایت الزامی است.')
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        try:
            validator = URLValidator(schemes=['http', 'https'])
            validator(url)
        except ValidationError:
            raise ValidationError('آدرس وب‌سایت معتبر نیست.')
        return url

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('عنوان وب‌سایت الزامی است.')
        return title

    class Meta:
        """fields to be used by form."""

        model = Website
        exclude = (
        )
        labels = {
            'captcha': "تشخیص ربات",
        }

        help_text = {'captcha': "انسان یا ربات؟"}