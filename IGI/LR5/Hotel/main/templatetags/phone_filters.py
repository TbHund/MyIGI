from django import template
import re

register = template.Library()

@register.filter(name='phone_format')
def phone_format(phone_number):
    if not phone_number:
        return phone_number
    
    #удалить все что не цифра
    digits = ''.join(filter(str.isdigit, str(phone_number)))
    
    if len(digits) == 12 and digits.startswith('375'):
        return f'+375 ({digits[3:5]}) {digits[5:8]}-{digits[8:10]}-{digits[10:12]}'
    return phone_number 