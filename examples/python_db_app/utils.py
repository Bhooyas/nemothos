import hashlib
import time

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def process_data(data):
    start = time.time()

    while time.time() - start < 0.1:
        pass

    return data.upper()

def add_item(item, items=[]):
    items.append(item)
    return items