"""
Compatibility library: {% load jalali_filters %}

Re-exports Jalali-related filters from farsi_tags so existing templates
(detail.html, admin_dashboard.html, user_dashboard.html) keep working
after the farsi + FarsiSaz merge.
"""

from django import template

from farsi.templatetags.farsi_tags import (
    # jalali,
    to_jalali,
    to_jalali_datetime,
    # to_jalali_persian,
    to_jalali_relative,
    to_jalali_short,
    persian_weekday,
)

register = template.Library()

register.filter('to_jalali', to_jalali)
register.filter('to_jalali_datetime', to_jalali_datetime)
register.filter('to_jalali_short', to_jalali_short)
register.filter('to_jalali_relative', to_jalali_relative)
# register.filter('to_jalali_persian', to_jalali_persian)
# register.filter('jalali', jalali)
register.filter('persian_weekday', persian_weekday)
