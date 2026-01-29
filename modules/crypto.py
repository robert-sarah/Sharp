"""Encryption and Hashing utilities for Sharp"""
import hashlib
import base64

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def sha1(text):
    return hashlib.sha1(text.encode()).hexdigest()

def md5(text):
    return hashlib.md5(text.encode()).hexdigest()

def base64_encode(text):
    return base64.b64encode(text.encode()).decode()

def base64_decode(encoded):
    try:
        return base64.b64decode(encoded).decode()
    except:
        return None

def hash_password(password):
    return sha256(password)

def verify_password(password, hash_val):
    return sha256(password) == hash_val
