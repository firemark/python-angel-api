from .api import api
from .db import Database
from . import config

from itertools import count
from datetime import datetime, timedelta
from time import sleep

import logging


log = logging.getLogger("angelo-api")


class AngelService(object):

    watchdog_counter = 0
    requests_counter = 0
    last_time = None
    continuous = False
    is_reset = False
    start = 1
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"
    max_id = 1

    def __init__(self, start=1, continuous=False):
        self.start = start
        self.continuous = continuous

        if config.has_account:
            api.get_access_token()

        if not config.brute_force:
            self.last_time = datetime.now()

        resp = Database.get(index=config.index_config_name, doc_type="cfg",
                            id="ids")

        db_max_id = resp["max_id"] if resp is not None else 1

        self.max_id = max(db_max_id, api.get_max_id())

    def exiting_ids(self):
        """Generator sends ids to get and save to database"""

        while True:
            for i in count(self.start):

                #save max_id every 20 cycle
                if not i % 20:
                    resp = Database.get(index=config.index_config_name,
                                        doc_type="cfg",
                                        id="ids")

                    new_max_id = resp["max_id"] if resp is not None else 1
                    if new_max_id < self.max_id:
                        Database.index(data={"max_id": self.max_id}, id="ids",
                                       index=config.index_config_name,
                                       doc_type="cfg")
                    else:
                        self.max_id = new_max_id

                if (self.max_id < i or
                        not Database.exists(id=i, doc_type="not_exists")):
                    yield i

                if self.is_reset:
                    self.is_reset = False

                    if not self.continuous:
                        raise StopIteration()
                    else:
                        break

    def reset(self):
        """set flag is_reset to true and reset counters"""
        self.watchdog_counter = 0
        self.is_reset = True
        if self.continuous:
            log.info("Return to id %d", self.start)

    def increase_watchdog(self):
        self.watchdog_counter += 1

    def execute_watchdog(self):
        if self.watchdog_counter >= config.watchdog_reset:
            log.info("Watchdog activated.")
            self.reset()

    def increase_request_counter(self):

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
        """download startup from api"""

        self.increase_request_counter()
        self.increase_watchdog()

        log.info("Download startup - id: %d", i)
        data = api.get_startup(i)

        self.execute_watchdog()

        return data

    @classmethod
    def convert_date(cls, dct):
        return datetime.strptime(dct["updated_at"], cls.datetime_format)

    def add_to_db(self, i, resp):

        if not resp:
            log.warning("id %d not found", i)
            Database.index(id=i, data={"hidden": False},
                           doc_type="not_exists")
            return False

        if self.max_id < i:
            self.max_id = i
        self.watchdog_counter = 0

        if resp["hidden"]:
            log.warning("id %d is a hidden office", i)
            Database.index(id=i, data={"hidden": True},
                           doc_type="not_exists")
            return False

        data = Database.get(id=i, doc_type="data")

        if data is None:
            Database.index(id=i, data=resp)
        else:
            data_date = self.convert_date(data)
            resp_date = self.convert_date(resp)
            if data_date > resp_date:
                Database.index(id=i, data=resp)

        return True