from .db import Database
from .api import get_startup, get_access_token
from . import config

from itertools import count
from requests.exceptions import HTTPError
from datetime import datetime, timedelta
from time import sleep

import logging

log = logging.getLogger("angelo-api")


def run(start=1):

    watchdog_counter = 0
    requests_counter = 0

    log.info("Start.")

    if config.has_account:
        get_access_token()

    if not config.brute_force:
        last_time = datetime.now()

    while True:
        for i in count(start):
            try:

                watchdog_counter += 1
                if watchdog_counter > config.watchdog_reset:
                    log.info("Watchdog activated. Return to id %d", start)
                    watchdog_counter = 0
                    break


                if not config.brute_force:
                    requests_counter += 1
                    if requests_counter > config.requests_per_hour:
                        last_time += timedelta(hours=1)
                        delta = last_time - datetime.now()

                        if delta.days >= 0:
                            log.info(
                                "The number of requests has "
                                "reached the limit (%d). "
                                "Waiting %dm %ds",
                                config.requests_per_hour,
                                delta.seconds / 60,
                                delta.seconds % 60
                            )
                            sleep(delta.seconds)
                            requests_counter = 0

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
                else:
                    watchdog_counter = 0
                    if resp["hidden"]:
                        log.warning("id %d is a hidden office", i)
                    else:
                        Database.index(id=resp["id"], data=resp)
