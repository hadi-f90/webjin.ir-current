# directory/forms.py
from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import Website
from taggit.models import Tag  # Import from taggit, not local
from captcha.fields import CaptchaField  # <--- 1. Import this

class WebsiteSubmitForm(forms.ModelForm):
    custom_slug = forms.SlugField(
        required=False,
        label='اسلاگ سفارشی',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'my-website'})
    )
    tags_input = forms.CharField(
        required=False,
        label='برچسب‌ها',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'برچسب را تایپ کنید... (با کاما جدا کنید)',
            'id': 'tagInput',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Website
        fields = ['title', 'url'] #  only model fields not ['title', 'custom_slug', 'url', 'description', 'category', 'owner_name', 'owner_email', 'hide_owner_info']
        # # captcha stays as an extra form field with its own label= on CaptchaField(...)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'عنوان وب‌سایت'})
        self.fields['url'].widget.attrs.update({'class': 'form-control', 'placeholder': 'example.com'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 4, 'placeholder': 'توضیحات...'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['owner_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'نام شما'})
        self.fields['owner_email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'ایمیل شما'})
        self.fields['hide_owner_info'].widget.attrs.update({'class': 'form-check-input mt-2'})

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

    def clean_custom_slug(self):
        slug = self.cleaned_data.get('custom_slug', '').strip()
        if slug:
            from django.utils.text import slugify
            slug = slugify(slug)
            if Website.objects.filter(slug=slug).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise ValidationError('این اسلاگ قبلاً استفاده شده است.')
        return slug

    def save(self, commit=True):
        website = super().save(commit=False)

        # Handle custom slug
        custom_slug = self.cleaned_data.get('custom_slug')
        if custom_slug:
            from django.utils.text import slugify
            website.slug = slugify(custom_slug)
            base_slug = website.slug
            if Website.objects.exclude(pk=website.pk).filter(slug=base_slug).exists():
                import uuid
                website.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

        # Handle tags from taggit
        tags_input = self.cleaned_data.get('tags_input', '')
        if tags_input:
            # taggit expects a string of comma-separated tags
            website.tags.set(tags_input.split(','))

        if commit:
            website.save()
            # taggit handles the many-to-many table automatically

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