# farsi/templatetags/farsi_tags.py
"""
تگ‌ها و فیلترهای قالب فارسی
"""

from django import template
from django.utils.safestring import mark_safe
import jdatetime
from datetime import datetime, date, timedelta
import re

register = template.Library()


# =============================================================================
# تاریخ جلالی
# =============================================================================

@register.filter
def to_jalali(date_obj):
    """
    تبدیل تاریخ میلادی به جلالی

    Args:
        date_obj: تاریخ میلادی (date یا datetime)

    Returns:
        رشته تاریخ جلالی به فرمت YYYY/MM/DD

    مثال:
        >>> to_jalali(date(2024, 1, 15))
        '1402/10/25'
    """
    if not date_obj:
        return ''

    try:
        if isinstance(date_obj, datetime):
            jalali = jdatetime.datetime.fromgregorian(datetime=date_obj)
            return jalali.strftime('%Y/%m/%d')
        elif isinstance(date_obj, date):
            jalali = jdatetime.date.fromgregorian(date=date_obj)
            return jalali.strftime('%Y/%m/%d')
        else:
            return ''
    except (ValueError, TypeError, AttributeError):
        return ''


@register.filter
def to_jalali_datetime(datetime_obj):
    """
    تبدیل تاریخ و زمان میلادی به جلالی

    Args:
        datetime_obj: تاریخ و زمان میلادی

    Returns:
        رشته تاریخ و زمان جلالی به فرمت YYYY/MM/DD - HH:MM

    مثال:
        >>> to_jalali_datetime(datetime(2024, 1, 15, 14, 30))
        '1402/10/25 - 14:30'
    """
    if not datetime_obj:
        return ''

    try:
        if isinstance(datetime_obj, datetime):
            jalali = jdatetime.datetime.fromgregorian(datetime=datetime_obj)
            return jalali.strftime('%Y/%m/%d - %H:%M')
        elif isinstance(datetime_obj, date):
            jalali = jdatetime.date.fromgregorian(date=datetime_obj)
            return jalali.strftime('%Y/%m/%d')
        else:
            return ''
    except (ValueError, TypeError, AttributeError):
        return ''


@register.filter
def to_jalali_short(date_obj):
    """
    تبدیل به فرمت کوتاه جلالی

    Args:
        date_obj: تاریخ میلادی

    Returns:
        رشته تاریخ کوتاه به فرمت MM/DD

    مثال:
        >>> to_jalali_short(date(2024, 1, 15))
        '10/25'
    """
    if not date_obj:
        return ''

    try:
        if isinstance(date_obj, datetime):
            jalali = jdatetime.datetime.fromgregorian(datetime=date_obj)
        elif isinstance(date_obj, date):
            jalali = jdatetime.date.fromgregorian(date=date_obj)
        else:
            return ''

        return jalali.strftime('%m/%d')
    except (ValueError, TypeError, AttributeError):
        return ''


@register.filter
def to_jalali_relative(date_obj):
    """
    تبدیل به زمان نسبی فارسی

    Args:
        date_obj: تاریخ میلادی

    Returns:
        رشته زمان نسبی فارسی

    مثال:
        >>> to_jalali_relative(datetime.now() - timedelta(hours=2))
        '۲ ساعت پیش'
    """
    if not date_obj:
        return ''

    try:
        # تبدیل به datetime اگر date باشد
        if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
            date_obj = datetime.combine(date_obj, datetime.min.time())

        # زمان فعلی
        now = datetime.now()

        # تفاوت زمانی
        diff = now - date_obj

        seconds = diff.total_seconds()

        # اعداد فارسی
        def to_p(num):
            persian_nums = '۰۱۲۳۴۵۶۷۸۹'
            eng_nums = '0123456789'
            return str(num).translate(str.maketrans(eng_nums, persian_nums))

        # کمتر از یک دقیقه
        if seconds < 60:
            return 'همین الان'

        # کمتر از یک ساعت
        if seconds < 3600:
            minutes = int(seconds / 60)
            return f'{to_p(minutes)} دقیقه پیش'

        # کمتر از یک روز
        if seconds < 86400:
            hours = int(seconds / 3600)
            return f'{to_p(hours)} ساعت پیش'

        # دیروز
        if seconds < 172800:  # 2 days
            return 'دیروز'

        # کمتر از یک هفته
        if seconds < 604800:  # 7 days
            days = int(seconds / 86400)
            return f'{to_p(days)} روز پیش'

        # کمتر از یک ماه
        if seconds < 2592000:  # 30 days
            weeks = int(seconds / 604800)
            return f'{to_p(weeks)} هفته پیش'

        # کمتر از یک سال
        if seconds < 31536000:  # 365 days
            months = int(seconds / 2592000)
            return f'{to_p(months)} ماه پیش'

        # بیش از یک سال
        years = int(seconds / 31536000)
        return f'{to_p(years)} سال پیش'

    except (ValueError, TypeError, AttributeError):
        return ''


# =============================================================================
# اعداد هندی
# =============================================================================

@register.filter
def to_hindi(number):
    """
    تبدیل اعداد به رقم‌های هندی (فارسی)

    Args:
        number: عدد (integer, float, یا string)

    Returns:
        رشته عدد با رقم‌های هندی

    مثال:
        >>> to_hindi(12345)
        '۱۲۳۴۵'
        >>> to_hindi('99.50')
        '۹۹.۵۰'
    """
    if number is None or number == '':
        return ''

    persian_nums = '۰۱۲۳۴۵۶۷۸۹'
    eng_nums = '0123456789'

    try:
        # تبدیل به رشته
        num_str = str(number)

        # جایگزینی اعداد
        trans_table = str.maketrans(eng_nums, persian_nums)
        return num_str.translate(trans_table)
    except (ValueError, TypeError):
        return ''


@register.filter
def to_hindi_with_comma(number):
    """
    تبدیل اعداد به هندی با جداکننده هزارگان

    Args:
        number: عدد (integer, float, یا string)

    Returns:
        رشته عدد با رقم‌های هندی و جداکننده

    مثال:
        >>> to_hindi_with_comma(1000)
        '۱,۰۰۰'
        >>> to_hindi_with_comma(1234567)
        '۱,۲۳۴,۵۶۷'
    """
    if number is None or number == '':
        return ''

    try:
        # تبدیل به عدد صحیح یا اعشاری
        if isinstance(number, str):
            # حذف کامای موجود
            number = number.replace(',', '')
            number = float(number) if '.' in number else int(number)

        # فرمت‌بندی با کاما
        if isinstance(number, float):
            formatted = f"{number:,.2f}"
        else:
            formatted = f"{number:,}"

        # تبدیل به اعداد هندی
        return to_hindi(formatted)
    except (ValueError, TypeError):
        return to_hindi(str(number))


# =============================================================================
# متن فارسی
# =============================================================================

@register.filter
def persianize(text):
    """
    تبدیل کاراکترهای عربی به فارسی

    تبدیل‌ها:
        ي → ی
        ك → ک
        ة → ه
        ۀ → ه
        ؤ → و
        ئ → ی
        أ → ا
        إ → ا
        آ → ا
        ة → ه

    Args:
        text: متن ورودی

    Returns:
        متن با کاراکترهای فارسی

    مثال:
        >>> persianize('سلام عليكم')
        'سلام علیکم'
    """
    if not text:
        return ''

    arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
    text = arabic_diacritics.sub('', text)

    # نقشه تبدیل عربی به فارسی
    conversion_map = {
        'ي': 'ی',
        'ك': 'ک',
        'ة': 'ه',
        'ۀ': 'ه',
        'ؤ': 'و',
        'ئ': 'ی',
        'أ': 'ا',
        'إ': 'ا',
        'آ': 'ا',
        '٠': '۰',
        '١': '۱',
        '٢': '۲',
        '٣': '۳',
        '٤': '۴',
        '٥': '۵',
        '٦': '۶',
        '٧': '۷',
        '٨': '۸',
        '٩': '۹',
    }

    result = text
    for arabic, persian in conversion_map.items():
        result = result.replace(arabic, persian)

    return result


@register.filter
def truncate_persian(text, length):
    """
    برش متن فارسی با سه‌نقطه مناسب

    Args:
        text: متن ورودی
        length: طول حداکثر

    Returns:
        متن بریده شده با سه‌نقطه فارسی

    مثال:
        >>> truncate_persian('این یک متن بلند است', 10)
        'این یک متن...'
    """
    if not text:
        return ''

    text = str(text)

    if len(text) <= length:
        return text

    # برش متن
    truncated = text[:length]

    # حذف فضای خالی آخر کلمه
    truncated = truncated.rstrip()

    # پیدا کردن آخرین فضای خالی برای برش کلمه کامل
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]

    # سه‌نقطه فارسی
    return truncated + '…'


@register.filter
def text_align(text):
    """
    تعیین جهت متن بر اساس محتوا

    Args:
        text: متن ورودی

    Returns:
        'right' برای متن فارسی
    """
    if not text:
        return 'right'

    # کاراکترهای فارسی
    persian_chars = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')

    if persian_chars.search(str(text)):
        return 'right'

    return 'left'


@register.filter
def rtl_class(text):
    """
    برگرداندن کلاس RTL برای متن فارسی

    Args:
        text: متن ورودی

    Returns:
        'rtl' اگر متن فارسی باشد، در غیر این صورت ''
    """
    if not text:
        return ''

    persian_chars = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')

    if persian_chars.search(str(text)):
        return 'rtl'

    return 'ltr'


# =============================================================================
# لیست و تکرار
# =============================================================================

@register.simple_tag
def persian_list(items, conjunction='و'):
    """
    اتصال آیتم‌های لیست با حرف فارسی

    Args:
        items: لیست آیتم‌ها
        conjunction: حرف ربط (پیش‌فرض: 'و')

    Returns:
        رشته متصل شده

    مثال:
        >>> persian_list(['آب', 'باد', 'خاک'])
        'آب، باد و خاک'
        >>> persian_list(['اول', 'دوم', 'سوم']، 'یا')
        'اول، دوم یا سوم'
    """
    if not items:
        return ''

    if not isinstance(items, (list, tuple)):
        items = list(items)

    if len(items) == 0:
        return ''

    if len(items) == 1:
        return str(items[0])

    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"

    # بیش از دو آیتم
    first_items = '، '.join(str(item) for item in items[:-1])
    last_item = str(items[-1])

    return f"{first_items} {conjunction} {last_item}"


@register.simple_tag
def persian_ordinal(number):
    """
    تبدیل عدد به ترتیب فارسی

    Args:
        number: عدد

    Returns:
        عدد ترتیبی فارسی

    مثال:
        >>> persian_ordinal(1)
        'اول'
        >>> persian_ordinal(2)
        'دوم'
        >>> persian_ordinal(3)
        'سوم'
    """
    if number is None:
        return ''

    ordinals = {
        1: 'اول',
        2: 'دوم',
        3: 'سوم',
        4: 'چهارم',
        5: 'پنجم',
        6: 'ششم',
        7: 'هفتم',
        8: 'هشتم',
        9: 'نهم',
        10: 'دهم',
    }

    if number in ordinals:
        return ordinals[number]

    # اعداد بزرگ‌تر
    return persian_number_word(number)+'م'


@register.simple_tag
def persian_number_word(number):
    """
    تبدیل عدد به حروف فارسی

    Args:
        number: عدد

    Returns:
        عدد به حروف

    مثال:
        >>> persian_number_word(100)
        'صد'
        >>> persian_number_word(21)
        'بیست و یک'
    """
    if number is None:
        return ''

    try:
        number = int(number)
    except (ValueError, TypeError):
        return ''

    # اعداد یک رقمی
    ones = ['صفر', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه']

    # اعداد دو رقمی
    tens = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']

    # اعداد خاص
    teens = ['ده', 'یازده', 'دوازده', 'سیزده', 'چهارده', 'پانزده', 'شانزده',
             'هفده', 'هجده', 'نوزده']



    if number == 0:
        return 'صفر'

    if number < 10:
        return ones[number]

    if number < 20:
        return teens[number - 10]

    if number < 100:
        ten = number // 10
        one = number % 10
        if one == 0:
            return tens[ten]
        return f"{tens[ten]} و {ones[one]}"

    if number < 1000:
        hundred = number // 100
        remainder = number % 100
        if hundred == 1:
            result = 'صد'
        elif hundred == 2:
            result = 'دویست'
        elif hundred == 3:
            result = 'سیصد'
        else:
            result = f"{ones[hundred]}صد"

        if remainder > 0:
            result += f" و {persian_number_word(remainder)}"
        return result

    # اعداد بزرگ‌تر
    return to_hindi(number)


# =============================================================================
# ابزارهای کمکی
# =============================================================================

@register.filter
def persian_currency(amount, currency='تومان'):
    """
    فرمت‌بندی پول فارسی

    Args:
        amount: مبلغ
        currency: واحد پول

    Returns:
        رشته مبلغ فارسی

    مثال:
        >>> persian_currency(15000)
        '۱۵,۰۰۰ تومان'
    """
    if amount is None:
        return ''

    formatted = to_hindi_with_comma(amount)
    return f"{formatted} {currency}"


@register.filter
def persian_phone(phone):
    """
    فرمت‌بندی شماره تلفن ایران
    """
    if not phone:
        return ''

    # حذف کاراکترهای غیر عددی
    phone = re.sub(r'\D', '', str(phone))

    # شماره موبایل ۱۰ رقمی: 0912-123-4567
    if len(phone) == 11 and phone.startswith('09'):
        return f"{to_hindi(phone[:4])}-{to_hindi(phone[4:7])}-{to_hindi(phone[7:])}"

    # شماره با +98: +98-91-2123-4567
    if len(phone) == 12 and phone.startswith('98'):
        return f"+{to_hindi(phone[:2])}-{to_hindi(phone[2:4])}-{to_hindi(phone[4:7])}-{to_hindi(phone[7:])}"

    # کل شماره با +: +98 912 123 4567
    if len(phone) > 10 and phone.startswith('98'):
        return f"+{to_hindi(phone)}"

    return to_hindi(phone)


@register.filter
def persian_weekday(date_obj):
    """
    نام روز هفته به فارسی

    Args:
        date_obj: تاریخ

    Returns:
        نام روز هفته

    مثال:
        >>> persian_weekday(date(2024, 1, 15))
        'یکشنبه'
    """
    if not date_obj:
        return ''

    try:
        if isinstance(date_obj, datetime):
            jalali = jdatetime.datetime.fromgregorian(datetime=date_obj)
        elif isinstance(date_obj, date):
            jalali = jdatetime.date.fromgregorian(date=date_obj)
        else:
            return ''

        weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
        return weekdays[jalali.weekday()]
    except (ValueError, TypeError, AttributeError):
        return ''

from urllib.parse import parse_qs, urlencode, urlparse


@register.filter
def remove_get_param(url, param):
    """Remove a specific parameter from URL query string."""

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    query_params.pop(param, None)
    new_query = urlencode(query_params, doseq=True)
    return parsed._replace(query=new_query).geturl()