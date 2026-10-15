import time
from collections import deque

START = time.time()
request_total = 0
logs: deque = deque(maxlen=2000)
