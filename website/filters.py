from datetime import datetime

def strftime(value, format_string):
    if isinstance(value, datetime):
        return value.strftime(format_string)
    return value

def get_plural_form(n, form1, form2, form5):
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} {form1}"
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return f"{n} {form2}"
    else:
        return f"{n} {form5}"