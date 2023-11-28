from datetime import datetime

def strftime(value, format_string):
    if isinstance(value, datetime):
        return value.strftime(format_string)
    return value