from .api import get_startup, get_access_token
from .db import Database
from . import config

from itertools import count
from datetime import datetime, timedelta
from time import sleep
import logging


log = logging.getLogger("angelo-api")

class WatchdogError(Exception):
    pass


class AngelService(object):

    watchdog_counter = 0
    requests_counter = 0
    last_time = None
    start = 1
    setup = False

    def __init__(self, start=1):
        self.start = start

        if config.has_account:
            get_access_token()

        if not config.brute_force:
            self.last_time = datetime.now()

    def exists_ids(self):
        for i in count(self.start):
            if not Database.exists(id=i, doc_type="not_exists"):
                yield i

    def increase_watchdog(self):
        self.watchdog_counter += 1

        if self.watchdog_counter > config.watchdog_reset:
            log.info("Watchdog activated. Return to id %d", start)
            self.watchdog_counter = 0
            raise WatchdogError()

    def increate_request_counter(self):

        if not config.brute_force:
            self.requests_counter += 1
            if self.requests_counter > config.requests_per_hour:
                self.last_time += timedelta(hours=1)
                delta = self.last_time - datetime.now()

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
                    self.requests_counter = 0

    def get(self, i):

        self.increase_watchdog()
        self.increate_request_counter()

        log.info("Download startup - id: %d", i)
        return get_startup(i)

    def add_to_db(self, i, resp):

        if not resp:
            log.warning("id %d not found", i)
            Database.index(id=i, data={"hidden": False},
                           doc_type="not_exists")
        else:
            self.watchdog_counter = 0
            if resp["hidden"]:
                log.warning("id %d is a hidden office", i)
                Database.index(id=i, data={"hidden": True},
                               doc_type="not_exists")
            else:
                Database.index(id=i, data=resp)