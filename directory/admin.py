from django.contrib import admin
from .models import Category, Rating, Report, Review, Website


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'slug',
        'category',
        'status',
        'average_rating',
        'total_ratings',
        'created_at',
    ]
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'url', 'description']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at', 'average_rating', 'total_ratings']
    # taggit provides a widget automatically in admin if installed correctly

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['website', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['website__title', 'user__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['website', 'user', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['website__title', 'user__username', 'content']
    list_editable = ['is_approved']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['website', 'user', 'report_type', 'is_resolved', 'created_at']
    list_filter = ['report_type', 'is_resolved', 'created_at']
    search_fields = ['website__title', 'user__username']
    list_editable = ['is_resolved']