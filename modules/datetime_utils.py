"""Datetime utilities for Sharp"""
from datetime import datetime, timedelta
import time

def current_timestamp():
    return int(time.time())

def current_datetime():
    return datetime.now().isoformat()

def timestamp_to_datetime(ts):
    return datetime.fromtimestamp(ts).isoformat()

def datetime_to_timestamp(dt_string):
    try:
        dt = datetime.fromisoformat(dt_string)
        return int(dt.timestamp())
    except:
        return None

def days_between(date1, date2):
    try:
        d1 = datetime.fromisoformat(date1)
        d2 = datetime.fromisoformat(date2)
        return abs((d2 - d1).days)
    except:
        return None

def add_days(date_string, days):
    try:
        dt = datetime.fromisoformat(date_string)
        new_dt = dt + timedelta(days=days)
        return new_dt.isoformat()
    except:
        return None

def format_date(date_string, format_str='%Y-%m-%d'):
    try:
        dt = datetime.fromisoformat(date_string)
        return dt.strftime(format_str)
    except:
        return None
