from django.contrib import admin
from .forms import WebsiteAdminForm
from .models import Category, Website


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    form = WebsiteAdminForm
    list_display = ['title', 'url', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'url', 'description']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_websites', 'reject_websites']

    @staticmethod
    def approve_websites(request, queryset):
        queryset.update(status='approved')
    approve_websites.short_description = "Mark selected websites as approved"

    @staticmethod
    def reject_websites(request, queryset):
        queryset.update(status='rejected')
    reject_websites.short_description = "Mark selected websites as rejected"