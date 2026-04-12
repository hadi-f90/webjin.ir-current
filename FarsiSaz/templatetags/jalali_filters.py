import jdatetime
from django import template

register = template.Library()

PERSIAN_MONTHS = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]

@register.filter
def to_jalali_persian(value, fmt="{day} {month_name} {year}"):
    """
    Convert Gregorian datetime/date to Jalali with Persian month name.
    Default output example: 20 فروردین 1405
    """
    if not value:
        return ""

    try:
        j = jdatetime.datetime.fromgregorian(datetime=value)

        month_name = PERSIAN_MONTHS[j.month - 1]

        return fmt.format(
            day=j.day,
            month=j.month,
            month_name=month_name,
            year=j.year,
            hour=getattr(j, "hour", 0),
            minute=getattr(j, "minute", 0),
            second=getattr(j, "second", 0),
        )
    except Exception:
        return value

@register.filter
def to_jalali(value, fmt="%Y/%m/%d"):
    """
    Convert a Gregorian datetime/date to Jalali.
    Supports datetime, date, and None-safe.
    Default format: 1405/01/20
    """
    if not value:
        return ""

    # If value is a datetime, include time
    if hasattr(value, "year"):
        try:
            j_date = jdatetime.datetime.fromgregorian(
                year=value.year,
                month=value.month,
                day=value.day,
                hour=getattr(value, "hour", 0),
                minute=getattr(value, "minute", 0),
                second=getattr(value, "second", 0),
            )
            return j_date.strftime(fmt)
        except Exception:
            return value
    return value

@register.filter
def jalali(value, fmt="%Y/%m/%d"):
    if not value:
        return ""
    try:
        j = jdatetime.datetime.fromgregorian(datetime=value)
        return j.strftime(fmt)
    except Exception:
        return value