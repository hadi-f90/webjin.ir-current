# farsi/templatetags/farsi.py
"""
تگ‌های قالب فارسی
"""

from django import template
from django.utils.safestring import mark_safe
from farsi.templatetags.utils import to_persian_num, to_english_num

register = template.Library()


@register.filter
def persian_num(value):
    """تبدیل اعداد به فارسی"""
    return to_persian_num(str(value))


@register.simple_tag
def persian_date(date, format='%Y/%m/%d'):
    """نمایش تاریخ به صورت جلالی"""
    from core.utils import format_jalali_date
    return format_jalali_date(date, format)


@register.filter
def english_num(value):
    """تبدیل اعداد فارسی به انگلیسی"""
    return to_english_num(str(value))