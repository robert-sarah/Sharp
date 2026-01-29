import base64
"""Compression utilities for Sharp"""
import zipfile
import gzip
import io

def compress_string(text, method='gzip'):
    try:
        if method == 'gzip':
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                f.write(text.encode())
            return base64.b64encode(buf.getvalue()).decode()
        return None
    except:
        return None

def decompress_string(compressed, method='gzip'):
    try:
        if method == 'gzip':
            import base64
            data = base64.b64decode(compressed)
            with gzip.GzipFile(fileobj=io.BytesIO(data), mode='rb') as f:
                return f.read().decode()
        return None
    except:
        return None

def zip_files(files, output_name):
    try:
        with zipfile.ZipFile(output_name, 'w') as zf:
            for file in files:
                zf.write(file)
        return True
    except:
        return False

def unzip_files(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_to)
        return True
    except:
        return False
