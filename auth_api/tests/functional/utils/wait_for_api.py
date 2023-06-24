import logging
import os
import sys
import time
from http import HTTPStatus

import requests

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    while True:
        try:
            response = requests.get(f"{test_settings.service_url}/hello_world")
            if response.status_code == HTTPStatus.OK:
                logger.info("services is available!!")
                break
        except requests.exceptions.ConnectionError:
            logger.info("api is unavailable. Wait...")
        time.sleep(2)
