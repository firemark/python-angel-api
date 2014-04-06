from . import config

from requests.exceptions import HTTPError, ConnectionError
from datetime import datetime, timedelta
from threading import Event
from time import sleep


import requests
import logging
import re

log = logging.getLogger("angelo-api")

account_event = Event()
code = None
re_max_id = re.compile(r"(\d+) Companies")


class AngelApi(object):

    requests_counter = 0
    last_time = datetime(2000, 1, 1)

    def __init__(self):

        if not config.brute_force:
            self.last_time = datetime.now()

    def increase_request_counter(self):

        if not config.brute_force:
            self.requests_counter += 1
            print(self.requests_counter)
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

    def get(self, *args, params=None):
        """
            GET https://api.angel.co/1/users/155?test=test
            get("users", 155, params={"test":"test"})
        """
        str_args = (str(arg) for arg in args)
        params = params or {}

        if config.access_token:
            params["access_token"] = config.access_token

        resp = requests.get(config.ANGEL_URL + "/".join(str_args),
                            params=params)

        if config.round_trip:
            sleep(3600 / config.requests_per_hour)

        self.increase_request_counter()

        log.debug("request url %s code %s", resp.url, resp.status_code)

        resp.raise_for_status()
        return resp.json()

    def get_access_token(self):

        print(
            "Link: https://angel.co/api/oauth/authorize?client_id={}"
            "&response_type=code".format(config.client_id)
        )
        print("waiting for a request…")

        account_event.wait()

        resp = requests.post("https://angel.co/api/oauth/token", params={
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        })

        resp.raise_for_status()
        access_token = resp.json()["access_token"]
        print("Access token is: ", access_token)

        config.access_token = access_token

    def get_max_id(self):
        """Get count of startups"""

        try:
            resp = requests.get("https://angel.co/companies")
            resp.raise_for_status()
        except ConnectionError:
            log.warning("Connection error in https://angel.co/companies")
            return 0

        searched = re_max_id.search(resp.text)
        if not searched:
            log.warning("Count of companies not found in "
                        "https://angel.co/companies")
            return 0

        return int(searched.group(1))

    def get_or_none(self, *args, params=None):
        try:
            return self.get(*args, params=params)
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e
            return None

    def get_founders_from_roles(self, roles, with_details=True):
        ids = (r["tagged"]["id"] for r in roles)

        params = {"include_details": "investor"} if with_details else None
        users = (
            self.get_or_none("users", user_id, params=params)
            for user_id in ids
        )

        return [user for user in users if user is not None]

    def get_startup(self, startup_id, with_founders=True, with_details=True):

        startup = self.get_or_none("startups", startup_id)
        if startup and not startup["hidden"]:
            roles = self.get("startups", startup_id, "roles")["startup_roles"]
            if with_founders:
                startup["founders"] = self.get_founders_from_roles(
                    roles,
                    with_details=with_details
                )

        return startup
