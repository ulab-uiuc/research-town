# frontend/backend/generator_function.py
import time

def data_generator(url):
    for i in range(1, 11):
        time.sleep(1)
        yield f"Processing {url}: step {i}\n"
