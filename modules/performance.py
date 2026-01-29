"""Performance monitoring utilities for Sharp"""
import time
import sys

class Timer:
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
    
    def start(self):
        self.start_time = time.time()
    
    def stop(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            print(f"{self.name} took {elapsed:.4f} seconds")
            return elapsed
        return 0

def measure_function(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed

def get_memory_usage():
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    except:
        return None

def profile_function(func):
    def wrapper(*args, **kwargs):
        timer = Timer(func.__name__)
        timer.start()
        result = func(*args, **kwargs)
        timer.stop()
        return result
    return wrapper
