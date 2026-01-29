"""Validation utilities for Sharp"""

def is_email(email):
    return '@' in email and '.' in email

def is_username(username):
    return len(username) >= 3 and len(username) <= 20

def is_strong_password(password):
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*' for c in password)
    return has_upper and has_lower and has_digit and has_special and len(password) >= 8

def is_phone_number(phone):
    digits_only = ''.join(c for c in phone if c.isdigit())
    return len(digits_only) >= 10

def is_credit_card(card_number):
    digits = ''.join(c for c in card_number if c.isdigit())
    return len(digits) in [13, 14, 15, 16]

def is_valid_url(url):
    return url.startswith('http://') or url.startswith('https://')

def sanitize_input(text):
    dangerous = ['<', '>', '"', "'", '&']
    for char in dangerous:
        text = text.replace(char, '')
    return text
