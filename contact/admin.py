from django.contrib import admin
from .models import Contact
from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin, TabularInlineJalaliMixin
# Register your models here.


class MyInlines1(TabularInlineJalaliMixin, admin.TabularInline):
    model = Contact


@admin.register(Contact)
class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'datetime_created',
                    'subject', 'message', 'spam_status')
    list_display_links = ('name', 'email', 'datetime_created',
                          'subject', 'message', 'spam_status')
    list_filter = ('spam_status', 'datetime_created', 'email', 'subject',
                   'name',  'message', )
    list_per_page = 20
    search_fields = ('name', 'email', 'subject', 'message',)
    ordering = ('datetime_created', 'name', 'email',
                'subject', 'message', 'spam_status')

    @admin.display(description='ایجاد', ordering='datetime_created')
    def get_created_jalali(self, obj):
        return datetime2jalali(obj.datetime_created).strftime('%a, %d %b %Y %H:%M:%S')
