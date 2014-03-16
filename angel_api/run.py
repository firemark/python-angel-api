from .db import Database
from .api import get_startup, get_access_token
from . import config

from itertools import count
from requests.exceptions import HTTPError

import logging

log = logging.getLogger("angelo-api")

def run(start=1):
    watchdog_counter = 0

    log.info("Start.")

    if config.has_account:
        get_access_token()

    while True:
        for i in count(start):
            try:

                watchdog_counter += 1
                if watchdog_counter > config.watchdog_reset:
                    log.info("Watchdog activated. Return to id %d", i)
                    break

                log.info("Download startup - id: %d", i)
                resp = get_startup(i)

            except HTTPError as e:
                http_resp = e.response
                code = http_resp.status_code
                log.error("HTTP Error (%i): %s", code, http_resp.json())
            except KeyboardInterrupt:
                log.info("Keyboard interrupt :(")
                exit()
            else:
                if not resp:
                    log.warning("id %d not found", i)
                elif resp["hidden"]:
                    log.warning("id %d is a hidden office", i)
                else:
                    watchdog_counter = 0
                    Database.index(id=resp["id"], data=resp)