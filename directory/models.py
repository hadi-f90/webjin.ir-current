import uuid

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Website(models.Model):
    STATUS_CHOICES = [
        ('pending', "در انتظار بررسی"),
        ('approved', "تأیید شده"),
        ('rejected', "رد شده"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    url = models.URLField()
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    owner_name = models.CharField(max_length=100)
    owner_email = models.EmailField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If no slug provided, generate from title
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug

            # Check if slug exists, if so, add UUID
            if Website.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

            self.slug = slug
        else:
            # If custom slug provided, make sure it's unique
            base_slug = slugify(self.slug)
            if Website.objects.exclude(pk=self.pk).filter(slug=base_slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            else:
                self.slug = base_slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('website_detail', kwargs={'slug': self.slug})