from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from taggit.managers import TaggableManager

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-folder', blank=True)  # Bootstrap icon

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_website_count(self):
        return self.website_set.filter(status='approved').count()

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
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='website_set'
    )

    # Use taggit's TaggableManager
    # Note: related_name='websites_tagged' is fine, but ensure it doesn't clash with other reverse relations
    tags = TaggableManager(blank=True, related_name='websites_tagged')

    # Owner info
    owner_name = models.CharField(max_length=100)
    owner_email = models.EmailField()
    hide_owner_info = models.BooleanField(default=False, verbose_name="مخفی کردن اطلاعات")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_websites'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Rating
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            # Avoid infinite loop if base_slug is empty
            if not slug:
                slug = f"website-{uuid.uuid4().hex[:8]}"
            if Website.objects.filter(slug=slug).exists():
                slug = f"{slug}-{uuid.uuid4().hex[:8]}"
            self.slug = slug
        else:
            # If slug is provided, ensure it's valid and unique
            base_slug = slugify(self.slug)
            if not base_slug:
                base_slug = f"website-{uuid.uuid4().hex[:8]}"
            if Website.objects.exclude(pk=self.pk).filter(slug=base_slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            else:
                self.slug = base_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('website_detail', kwargs={'slug': self.slug})

    def update_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            total = sum(r.rating for r in ratings)
            self.average_rating = total / ratings.count()
            self.total_ratings = ratings.count()
        else:
            self.average_rating = 0
            self.total_ratings = 0
        self.save(update_fields=['average_rating', 'total_ratings'])

class Rating(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['website', 'user']

    def __str__(self):
        return f"{self.website.title} - {self.rating} stars"

class Review(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} on {self.website.title}"

class Report(models.Model):
    REPORT_CHOICES = [
        ('broken', 'لینک خراب'),
        ('shutdown', 'وب‌سایت غیرفعال'),
        ('inappropriate', 'محتوای نامناسب'),
        ('scam', 'کلاهبرداری/فیشینگ'),
        ('other', 'دیگر'),
    ]
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_CHOICES)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.website.title}"