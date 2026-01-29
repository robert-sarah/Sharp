"""Threading utilities for Sharp"""
import threading
import time

class Thread:
    def __init__(self, target, name="Thread"):
        self.target = target
        self.name = name
        self.thread = None
    
    def start(self):
        self.thread = threading.Thread(target=self.target, name=self.name)
        self.thread.start()
    
    def join(self):
        if self.thread:
            self.thread.join()
    
    def is_alive(self):
        return self.thread.is_alive() if self.thread else False

class Lock:
    def __init__(self):
        self._lock = threading.Lock()
    
    def acquire(self):
        self._lock.acquire()
    
    def release(self):
        self._lock.release()

def create_thread(target):
    return Thread(target)

def create_lock():
    return Lock()

def sleep(seconds):
    time.sleep(seconds)
