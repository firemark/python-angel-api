from .db import Database

from . import config
from .angel import WatchdogError, AngelService

from requests.exceptions import HTTPError
from elasticsearch.exceptions import TransportError
import logging

log = logging.getLogger("angelo-api")


def run(start=1):

    watchdog_counter = 0
    requests_counter = 0

    log.info("Start.")
    service = AngelService(start=start)

    while True:
        for i in service.exists_ids():
            try:
                resp = service.get(i)
                service.add_to_db(i, resp)
            except HTTPError as e:
                http_resp = e.response
                code = http_resp.status_code
                log.error("HTTP Error (%i): %s", code, http_resp.json())

                if code in (408, 403):
                    break

            except TransportError as e:
                log.error("ES Error (%i): %s", e.status_code, e.error)

            except KeyboardInterrupt:
                log.info("Keyboard interrupt :(")
                exit()
            except WatchdogError:
                break

