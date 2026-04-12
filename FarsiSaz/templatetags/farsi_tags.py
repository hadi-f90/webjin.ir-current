"""Tags to convert Latin Numbers to Unicode Farsi counterparts."""
from django import template

register = template.Library()


FA_NUMERS = '۰۱۲۳۴۵۶۷۸۹'
EN_NUMBERS = '0123456789'
FA_CHARS = "؛،﷼٫؟"
EN_CHARS = ";,$.?"


@register.filter
def to_farsi(value):
    """Digit to digit conversion."""
    value = str(value)
    digit2digit_table = str.maketrans(EN_NUMBERS, FA_NUMERS)
    return value.translate(digit2digit_table)


@register.filter
def to_farsi_str(value):
    """Char to char conversion."""
    value = str(value)
    str2str_table = str.maketrans(EN_CHARS, FA_CHARS)
    return value.translate(str2str_table)

