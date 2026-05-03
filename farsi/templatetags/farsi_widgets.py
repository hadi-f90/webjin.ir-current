# farsi/templatetags/farsi_widgets.py
"""
ویجت‌های فرم فارسی
"""

from django import template

register = template.Library()


@register.inclusion_tag('farsi/bootstrap5_form.html')
def persian_form_field(field):
    """
    رندر فیلد فرم با برچسب و راهنمای فارسی

    Usage:
        {% load farsi_widgets %}
        {% persian_form_field form.field_name %}

    Args:
        field: فیلد فرم Django

    Returns:
        context شامل فیلد و اطلاعات اضافی
    """
    return {
        'field': field,
        'id': field.id_for_label,
        'label': field.label,
        'help_text': field.help_text,
        'errors': field.errors,
        'required': field.field.required,
        'class': 'is-invalid' if field.errors else '',
    }


@register.inclusion_tag('farsi/persian_datepicker.html')
def persian_datepicker(id, name, value=None, label='', required=False, help_text='', attrs=None):
    """
    تولید ورودی تاریخ جلالی با Persian Datepicker

    Usage:
        {% load farsi_widgets %}
        {% persian_datepicker 'birth_date' 'birth_date' user.birth_date 'تاریخ تولد' %}

    Args:
        id: شناسه input
        name: نام input
        value: مقدار پیش‌فرض
        label: برچسب فارسی
        required: آیا اجباری است
        help_text: متن راهنما
        attrs: ویژگی‌های اضافی HTML

    Returns:
        context برای قالب
    """
    # تبدیل مقدار به فرمت جلالی اگر datetime باشد
    display_value = ''
    if value:
        try:
            import jdatetime
            if hasattr(value, 'strftime'):
                # تاریخ میلادی
                if hasattr(value, 'hour'):
                    # datetime
                    jalali = jdatetime.datetime.fromgregorian(datetime=value)

                else:
                    # date
                    jalali = jdatetime.date.fromgregorian(date=value)

            else:

                display_value = jalali.strftime('%Y/%m/%d')
                display_value = str(value)
        except Exception:
            display_value = str(value) if value else ''

    # ویژگی‌های اضافی
    extra_attrs = ''
    if attrs:
        for key, val in attrs.items():
            extra_attrs += f' {key}="{val}"'

    return {
        'id': id,
        'name': name,
        'value': display_value,
        'label': label,
        'required': required,
        'help_text': help_text,
        'extra_attrs': extra_attrs,
    }


@register.inclusion_tag('farsi/persian_datetimepicker.html')
def persian_datetimepicker(
    id, name, value=None, label='', required=False, help_text='', attrs=None
):
    """
    تولید ورودی تاریخ و زمان جلالی

    Args:
        id: شناسه input
        name: نام input
        value: مقدار پیش‌فرض (datetime)
        label: برچسب فارسی
        required: آیا اجباری است
        help_text: متن راهنما
        attrs: ویژگی‌های اضافی

    Returns:
        context برای قالب
    """
    display_value = ''
    if value:
        try:

            if hasattr(value, 'strftime'):
                if hasattr(value, 'hour'):
                    jalali = jdatetime.datetime.fromgregorian(datetime=value)
                    display_value = jalali.strftime('%Y/%m/%d %H:%M')
                else:
                    jalali = jdatetime.date.fromgregorian(date=value)
                    display_value = jalali.strftime('%Y/%m/%d')
        except Exception:
            display_value = str(value) if value else ''

    extra_attrs = ''
    if attrs:
        for key, val in attrs.items():
            extra_attrs += f' {key}="{val}"'

    return {
        'id': id,
        'name': name,
        'value': display_value,
        'label': label,
        'required': required,
        'help_text': help_text,
        'extra_attrs': extra_attrs,
    }


@register.inclusion_tag('farsi/persian_textarea.html')
def persian_textarea(
    name, value=None, label='', rows=4, required=False, help_text='', placeholder='', attrs=None
):
    """
    تولید textarea فارسی

    Args:
        name: نام textarea
        value: مقدار پیش‌فرض
        label: برچسب
        rows: تعداد سطرها
        required: اجباری
        help_text: راهنما
        placeholder: متن راهنمای داخل فیلد
        attrs: ویژگی‌های اضافی

    Returns:
        context برای قالب
    """
    extra_attrs = ''
    if attrs:
        for key, val in attrs.items():
            extra_attrs += f' {key}="{val}"'

    return {
        'name': name,
        'value': value,
        'label': label,
        'rows': rows,
        'required': required,
        'help_text': help_text,
        'placeholder': placeholder,
        'extra_attrs': extra_attrs,
    }