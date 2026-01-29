"""Image processing utilities for Sharp"""
try:
    from PIL import Image
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False

def load_image(filepath):
    if not PIL_AVAILABLE:
        return None
    try:
        return Image.open(filepath)
    except:
        return None

def save_image(image, filepath):
    if not PIL_AVAILABLE:
        return False
    try:
        image.save(filepath)
        return True
    except:
        return False

def resize_image(image, width, height):
    if not PIL_AVAILABLE:
        return None
    try:
        return image.resize((width, height))
    except:
        return None

def get_image_size(filepath):
    if not PIL_AVAILABLE:
        return None
    try:
        img = Image.open(filepath)
        return (img.width, img.height)
    except:
        return None

def convert_image_format(input_path, output_path, format):
    if not PIL_AVAILABLE:
        return False
    try:
        img = Image.open(input_path)
        img.save(output_path, format=format)
        return True
    except:
        return False
