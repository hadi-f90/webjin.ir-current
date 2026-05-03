# core/utils.py
"""
ابزارهای کمکی پروژه راهنمای وب ایران
"""

import re

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.text import slugify


def get_client_ip(request: HttpRequest) -> str:
    """
    دریافت آدرس IP کاربر

    Args:
        درخواست HTTP

    Returns:
        آدرس IP کاربر
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def generate_slug(
    text: str, model_class: models.Model, field_name: str = 'slug', max_length: int = 50
) -> str:
    """
    تولید slug یکتا برای متن فارسی

    Args:
        text: متن ورودی
        model_class: کلاس مدل برای بررسی تکراری بودن
        field_name: نام فیلد slug در مدل
        max_length: حداکثر طول slug

    Returns:
        slug یکتا
    """
    # تبدیل به حروف کوچک
    slug = slugify(text)

    # اگر slug خالی بود، از متن پیش‌فرض استفاده کن
    if not slug:
        slug = 'item'

    # محدود کردن طول
    slug = slug[:max_length]

    # بررسی تکراری بودن
    queryset = model_class.objects.all()

    # حذف کاراکترهای غیر مجاز
    slug = re.sub(r'[^\w\-]', '', slug)
    slug = re.sub(r'-+', '-', slug)  # چند خط فاصله را یکی کن

    original_slug = slug
    counter = 1

    while queryset.filter(**{field_name: slug}).exists():
        slug = f"{original_slug}-{counter}"
        counter += 1

    return slug


def to_persian_num(num: int | str) -> str:
    """
    تبدیل اعداد انگلیسی به فارسی

    Args:
        num: عدد ورودی

    Returns:
        عدد به صورت فارسی
    """
    persian_nums = "۰۱۲۳۴۵۶۷۸۹"
    eng_nums = '0123456789'

    if isinstance(num, int):
        num = str(num)

    trans_table = str.maketrans(eng_nums, persian_nums)
    return num.translate(trans_table)


def to_english_num(num: str) -> int | str:
    """
    تبدیل اعداد فارسی به انگلیسی

    Args:
        num: عدد فارسی

    Returns:
        عدد انگلیسی
    """
    persian_nums = "۰۱۲۳۴۵۶۷۸۹"
    eng_nums = '0123456789'

    trans_table = str.maketrans(persian_nums, eng_nums)
    return num.translate(trans_table)


def send_email(
    subject: str, template: str, context: dict, to: list[str] | str, from_email: str = None
) -> bool:
    """
    ارسال ایمیل با قالب

    Args:
        subject: موضوع ایمیل
        template: مسیر قالب ایمیل
        context: context قالب
        to: گیرنده یا لیست گیرندگان
        from_email: آدرس فرستنده

    Returns:
        True اگر ارسال موفق باشد
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    # تبدیل به لیست اگر یک رشته باشد
    if isinstance(to, str):
        to = [to]

    # رندر قالب
    message = render_to_string(template, context)

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=to,
            html_message=message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # لاگ خطا در صورت نیاز
        print(f"Error sending email: {e}")
        return False


def format_jalali_date(date, format_string: str = '%Y/%m/%d') -> str:
    """
    فرمت‌بندی تاریخ به صورت جلالی

    Args:
        date: شیء تاریخ
        format_string: فرمت خروجی

    Returns:
        تاریخ فرمت‌بندی شده
    """
    try:
        import jdatetime
        if date:
            # تبدیل به جلالی
            jalali_date = jdatetime.datetime.fromgregorian(datetime=date)
            return jalali_date.strftime(format_string)
    except Exception:
        pass
    return ''


def truncate_persian(text: str, length: int = 100, suffix: str = '...') -> str:
    """
    برش متن فارسی با پشتیبانی از Unicode

    Args:
        text: متن ورودی
        length: طول حداکثر
        suffix: پسوند اضافه شده

    Returns:
        متن بریده شده
    """
    if len(text) <= length:
        return text

    # برش متن
    truncated = text[:length]

    # حذف فضای خالی آخر کلمه
    truncated = truncated.rsplit(' ', 1)[0]

    return truncated + suffix