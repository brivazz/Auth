import logging
import os
import sys
import time

from redis import Redis

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

if __name__ == "__main__":
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    while True:
        print("wait for redis startup....")
        logging.info("wait for redis startup....")
        if redis_client.ping():
            print("Redis startup!!")
            break
        time.sleep(1)
