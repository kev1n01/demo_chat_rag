import time

def stream_data(text, speed=0.08):
    for w in text.split(" "):
        yield w + " "
        time.sleep(speed)