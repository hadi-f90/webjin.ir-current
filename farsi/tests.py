# farsi/tests.py

from django.test import TestCase
from datetime import datetime, date, timedelta
from farsi.templatetags.farsi_tags import (
    to_hindi,
    to_hindi_with_comma,
    to_jalali,
    to_jalali_datetime,
    to_jalali_short,
    to_jalali_relative,
    persianize,
    truncate_persian,
    text_align,
    rtl_class,
    persian_list,
    persian_currency,
    persian_phone,
    persian_weekday,
)


class ToHindiFilterTestCase(TestCase):
    """تست فیلتر تبدیل اعداد به هندی"""

    def test_integer_to_hindi(self):
        """تست اعداد صحیح"""
        self.assertEqual(to_hindi(0), '۰')
        self.assertEqual(to_hindi(1), '۱')
        self.assertEqual(to_hindi(9), '۹')
        self.assertEqual(to_hindi(10), '۱۰')
        self.assertEqual(to_hindi(100), '۱۰۰')
        self.assertEqual(to_hindi(123456789), '۱۲۳۴۵۶۷۸۹')

    def test_float_to_hindi(self):
        """تست اعداد اعشاری"""
        self.assertEqual(to_hindi(10.5), '۱۰.۵')
        self.assertEqual(to_hindi(0.99), '۰.۹۹')
        self.assertEqual(to_hindi(1234.5678), '۱۲۳۴.۵۶۷۸')

    def test_string_to_hindi(self):
        """تست رشته‌های عددی"""
        self.assertEqual(to_hindi('123'), '۱۲۳')
        self.assertEqual(to_hindi('0'), '۰')
        self.assertEqual(to_hindi('999'), '۹۹۹')

    def test_none_to_hindi(self):
        """تست مقادیر خالی"""
        self.assertEqual(to_hindi(None), '')
        self.assertEqual(to_hindi(''), '')

    def test_with_comma(self):
        """تست اعداد با جداکننده هزارگان"""
        self.assertEqual(to_hindi_with_comma(1000), '۱,۰۰۰')
        self.assertEqual(to_hindi_with_comma(1000000), '۱,۰۰۰,۰۰۰')
        self.assertEqual(to_hindi_with_comma(1234567), '۱,۲۳۴,۵۶۷')
        self.assertEqual(to_hindi_with_comma(1000.50), '۱,۰۰۰.۵۰')


class ToJalaliFilterTestCase(TestCase):
    """تست فیلترهای تاریخ جلالی"""

    def test_to_jalali_date(self):
        """تست تبدیل تاریخ"""
        # 1402/10/25 = 2024/01/15
        result = to_jalali(date(2024, 1, 15))
        self.assertEqual(result, '1402/10/25')

    def test_to_jalali_datetime(self):
        """تست تبدیل تاریخ و زمان"""
        result = to_jalali_datetime(datetime(2024, 1, 15, 14, 30))
        self.assertEqual(result, '1402/10/25 - 14:30')

    def test_to_jalali_short(self):
        """تست فرمت کوتاه"""
        result = to_jalali_short(date(2024, 1, 15))
        self.assertEqual(result, '10/25')

    def test_to_jalali_none(self):
        """تست مقادیر خالی"""
        self.assertEqual(to_jalali(None), '')
        self.assertEqual(to_jalali(''), '')
        self.assertEqual(to_jalali_datetime(None), '')

    def test_to_jalali_relative(self):
        """تست زمان نسبی"""
        # همین الان
        now = datetime.now()
        self.assertEqual(to_jalali_relative(now), 'همین الان')

        # 2 ساعت پیش
        two_hours_ago = now - timedelta(hours=2)
        self.assertEqual(to_jalali_relative(two_hours_ago), '۲ ساعت پیش')

        # دیروز
        yesterday = now - timedelta(days=1)
        self.assertIn('دیروز', to_jalali_relative(yesterday))

        # 3 روز پیش
        three_days_ago = now - timedelta(days=3)
        self.assertEqual(to_jalali_relative(three_days_ago), '۳ روز پیش')


class PersianizeFilterTestCase(TestCase):
    """تست فیلتر فارسی‌سازی"""

    def test_ya_to_ye(self):
        """تست تبدیل ی عربی به ی فارسی"""
        self.assertEqual(persianize('سلام عليكم'), 'سلام علیکم')
        self.assertEqual(persianize('بيت'), 'بیت')

    def test_kaf_to_ke(self):
        """تست تبدیل ک عربی به ک فارسی"""
        self.assertEqual(persianize('كتاب'), 'کتاب')

    def test_ta_marbuta(self):
        """تست تبدیل تاء مربوطه"""
        # تاء مربوطه (ة) به ه تبدیل می‌شود، نه ت
        self.assertEqual(persianize('جميلة'), 'جمیله')
        self.assertEqual(persianize('حركة'), 'حرکه')
        self.assertEqual(persianize('حديقة'), 'حدیقه')

    def test_arabic_numbers(self):
        """تست تبدیل اعداد عربی به فارسی"""
        self.assertEqual(persianize('٠١٢٣'), '۰۱۲۳')
        self.assertEqual(persianize('٩٨٧'), '۹۸۷')

    def test_alef_variants(self):
        """تست واریانت‌های الف"""
        self.assertEqual(persianize("أهلاً"), "اهلا")  # اعراب حذف می‌شود ✓
        self.assertEqual(persianize("إسلام"), "اسلام")
        self.assertEqual(persianize("آب"), "اب")

    def test_persianize_none(self):
        """تست مقادیر خالی"""
        self.assertEqual(persianize(None), '')
        self.assertEqual(persianize(''), '')


class TruncatePersianTestCase(TestCase):
    """تست برش متن فارسی"""

    def test_short_text(self):
        """تست متن کوتاه"""
        text = 'این یک متن کوتاه است'
        result = truncate_persian(text, 50)
        self.assertEqual(result, text)

    def test_long_text(self):
        """تست متن بلند"""
        text = 'این یک متن بلند است که باید بریده شود'
        result = truncate_persian(text, 15)
        self.assertTrue(len(result) <= 18)
        self.assertTrue(result.endswith('…'))

    def test_word_boundary(self):
        """تست مرز کلمه"""
        text = 'این یک متن بلند است'
        result = truncate_persian(text, 8)
        # نباید کلمه را وسط برش دهد
        self.assertNotIn('متن ب', result)


class TextAlignTestCase(TestCase):
    """تست تعیین جهت متن"""

    def test_persian_text(self):
        """تست متن فارسی"""
        self.assertEqual(text_align('سلام'), 'right')
        self.assertEqual(text_align('این یک متن فارسی است'), 'right')

    def test_english_text(self):
        """تست متن انگلیسی"""
        self.assertEqual(text_align('Hello'), 'left')
        self.assertEqual(text_align('This is English'), 'left')

    def test_mixed_text(self):
        """تست متن مخلوط"""
        self.assertEqual(text_align('Hello سلام'), 'right')


class PersianListTestCase(TestCase):
    """تست لیست فارسی"""

    def test_empty_list(self):
        """تست لیست خالی"""
        self.assertEqual(persian_list([]), '')
        self.assertEqual(persian_list(None), '')

    def test_single_item(self):
        """تست یک آیتم"""
        self.assertEqual(persian_list(['آب']), 'آب')

    def test_two_items(self):
        """تست دو آیتم"""
        result = persian_list(['آب', 'باد'])
        self.assertEqual(result, 'آب و باد')

    def test_three_items(self):
        """تست سه آیتم"""
        # کامای بین آیتم‌ها باید فارسی باشد
        result = persian_list(['آب', 'باد', 'خاک'])
        self.assertEqual(result, 'آب، باد و خاک')

    def test_custom_conjunction(self):
        """تست حرف ربط سفارشی"""
        result = persian_list(['اول', 'دوم', 'سوم'], 'یا')
        self.assertEqual(result, 'اول، دوم یا سوم')


class PersianCurrencyTestCase(TestCase):
    """تست فرمت پول فارسی"""

    def test_currency(self):
        """تست فرمت پول"""
        self.assertEqual(persian_currency(1000), '۱,۰۰۰ تومان')
        self.assertEqual(persian_currency(50000), '۵۰,۰۰۰ تومان')

    def test_custom_currency(self):
        """تست واحد پول سفارشی"""
        self.assertEqual(persian_currency(100, 'ریال'), '۱۰۰ ریال')


class PersianPhoneTestCase(TestCase):
    """تست فرمت تلفن فارسی"""

    def test_mobile_number(self):
        """تست شماره موبایل"""
        result = persian_phone('09121234567')
        print(result)
        self.assertEqual(result, '۰۹۱۲-۱۲۳-۴۵۶۷')

    def test_with_plus(self):
        """تست شماره با پلاس"""
        result = persian_phone('+989121234567')
        self.assertIn('۹۸', result)


class PersianWeekdayTestCase(TestCase):
    """تست روز هفته"""

    def test_weekday(self):
        """تست روز هفته"""
        # 2024-01-14 = یکشنبه (Sunday)
        result = persian_weekday(date(2024, 1, 14))
        self.assertEqual(result, 'یکشنبه')

    def test_friday(self):
        """تست جمعه"""
        # 2024-01-19 = جمعه (Friday)
        result = persian_weekday(date(2024, 1, 19))
        self.assertEqual(result, 'جمعه')