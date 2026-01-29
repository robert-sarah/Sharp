"""HTTP Client for Sharp"""
import urllib.request
import json

def http_get(url):
    try:
        response = urllib.request.urlopen(url)
        return response.read().decode('utf-8')
    except:
        return None

def http_post(url, data):
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data)
        response = urllib.request.urlopen(req)
        return response.read().decode('utf-8')
    except:
        return None

def http_headers(url):
    try:
        response = urllib.request.urlopen(url)
        return dict(response.headers)
    except:
        return {}

def http_status(url):
    try:
        response = urllib.request.urlopen(url)
        return response.status
    except:
        return None
