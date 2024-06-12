import time

def stream_data(text, speed):
    for w in text.split(" "):
        yield w + " "
        time.sleep(speed)