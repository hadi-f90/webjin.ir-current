from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import Website, Tag


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
            'placeholder': 'برچسب را تایپ کنید...',
            'id': 'tagInput',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = Website
        fields = ['title', 'custom_slug', 'url', 'description', 'category', 'owner_name', 'owner_email', 'hide_owner_info']
    
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
        if self.cleaned_data.get('custom_slug'):
            from django.utils.text import slugify
            website.slug = slugify(self.cleaned_data['custom_slug'])
        
        if commit:
            website.save()
            tags_input = self.cleaned_data.get('tags_input', '')
            if tags_input:
                # Clear existing tags and add new ones
                website.tags.clear()
                tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    website.tags.add(tag)
        
        return website


def tag_suggestions(request):
    """AJAX endpoint for tag autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 1:
        return JsonResponse({'tags': []})
    
    tags = Tag.objects.filter(name__icontains=query)[:10]
    return JsonResponse({'tags': [{'id': t.id, 'name': t.name} for t in tags]})


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
