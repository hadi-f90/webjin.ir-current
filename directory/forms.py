# directory/forms.py
"""
Forms for WebJin directory app.

Phase 0 fix:
- WebsiteSubmitForm: full model fields restored (edit / full submit)
- QuickSubmitForm: Meta.fields = ['title', 'url'] only; captcha is an extra field
- tags.set() runs only after the Website row has a primary key
"""

from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.text import slugify

from .models import Website
from taggit.models import Tag
from captcha.fields import CaptchaField


class WebsiteSubmitForm(forms.ModelForm):
    """
    Full submit / edit form.
    Model fields via Meta; custom_slug and tags_input are extra non-model fields.
    """

    custom_slug = forms.SlugField(
        required=False,
        label='اسلاگ سفارشی',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'my-website'}
        ),
    )
    tags_input = forms.CharField(
        required=False,
        label='برچسب‌ها',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'برچسب را تایپ کنید... (با کاما جدا کنید)',
                'id': 'tagInput',
                'autocomplete': 'off',
            }
        ),
    )

    class Meta:
        model = Website
        fields = [
            'title',
            'url',
            'description',
            'category',
            'owner_name',
            'owner_email',
            'hide_owner_info',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widgets = {
            'title': {'class': 'form-control', 'placeholder': 'عنوان وب‌سایت'},
            'url': {'class': 'form-control', 'placeholder': 'example.com'},
            'description': {
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'توضیحات...',
            },
            'category': {'class': 'form-control'},
            'owner_name': {'class': 'form-control', 'placeholder': 'نام شما'},
            'owner_email': {'class': 'form-control', 'placeholder': 'ایمیل شما'},
            'hide_owner_info': {'class': 'form-check-input mt-2'},
        }
        for name, attrs in widgets.items():
            if name in self.fields:
                self.fields[name].widget.attrs.update(attrs)

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
            slug = slugify(slug)
            qs = Website.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('این اسلاگ قبلاً استفاده شده است.')
        return slug

    def save(self, commit=True):
        website = super().save(commit=False)

        custom_slug = self.cleaned_data.get('custom_slug')
        if custom_slug:
            website.slug = slugify(custom_slug)
            base_slug = website.slug
            if (
                Website.objects.exclude(pk=website.pk or 0)
                .filter(slug=base_slug)
                .exists()
            ):
                import uuid

                website.slug = f'{base_slug}-{uuid.uuid4().hex[:8]}'

        tags_input = self.cleaned_data.get('tags_input', '') or ''
        tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]

        if commit:
            website.save()
            # taggit requires a saved instance (pk) before .set()
            if tag_names:
                website.tags.set(tag_names)
            elif tags_input == '' and self.instance and self.instance.pk:
                # empty string from edit form can clear tags if UI sends empty
                pass
        else:
            # caller must save then apply tags
            self._pending_tags = tag_names

        return website


def tag_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 1:
        return JsonResponse({'tags': []})

    tags = Tag.objects.filter(name__icontains=query)[:10]
    return JsonResponse(
        {
            'tags': [
                {'id': t.id, 'name': t.name, 'slug': t.slug} for t in tags
            ]
        }
    )


class RatingForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, '⭐' * i) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'rating-star'}),
        label='امتیاز شما',
    )


class ReviewForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'نظر خود را بنویسید...',
            }
        ),
        label='نظر شما',
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
        label='نوع گزارش',
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'توضیحات بیشتر',
            }
        ),
        required=False,
        label='توضیحات',
    )


class QuickSubmitForm(forms.ModelForm):
    """
    Minimal public submit form for guests: title + url + captcha.
    View builds the Website instance manually from cleaned_data.
    """

    title = forms.CharField(
        max_length=200,
        label='عنوان وب‌سایت',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'مثال: فروشگاه آنلاین دیجی‌کالا',
            }
        ),
    )
    url = forms.CharField(
        label='آدرس وب‌سایت',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'example.com',
            }
        ),
    )
    captcha = CaptchaField(label='کد امنیتی')

    class Meta:
        model = Website
        fields = ['title', 'url']

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


class PublicWebsiteSubmitForm(WebsiteSubmitForm):
    """Public submit: full optional details + captcha (AJAX or classic POST)."""

    captcha = CaptchaField(
        label='کد امنیتی',
        error_messages={
            'invalid': 'کد امنیتی نادرست است.',
            'required': 'کد امنیتی الزامی است.',
        },
    )

    class Meta(WebsiteSubmitForm.Meta):
        fields = [
            'title',
            'url',
            'description',
            'category',
            'owner_name',
            'owner_email',
            'hide_owner_info',
        ]

