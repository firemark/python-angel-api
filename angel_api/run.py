from .db import Database

from . import config
from .angel import AngelService

from time import sleep
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError as RequestConnectionError
from elasticsearch.exceptions import (RequestError, NotFoundError,
                                      ConflictError, TransportError)

import logging

log = logging.getLogger("angelo-api")


def run(start=1, continuous=False):

    try:
        log.info("Start.")
        service = AngelService(start=start, continuous=continuous)

        for i in service.exiting_ids():
            try:
                resp = service.get(i)
                service.add_to_db(i, resp)

            except HTTPError as e:
                http_resp = e.response
                code = http_resp.status_code
                log.error("API HTTP Error (%i): %s", code, http_resp.json())

                if code in (408, 403):
                    service.reset()
            except RequestConnectionError as e:
                log.error("API Connection Error (%s), waiting %d seconds", e,
                          config.delay_connection)
                sleep(config.delay_connection)
            except (RequestError, NotFoundError, ConflictError) as e:
                log.error("ES HTTP Error (%i): %s", e.status_code, e.error)
            except TransportError as e:
                log.error("ES Critical Error (%s), waiting %d seconds", e,
                          config.delay_connection)
                sleep(config.delay_connection)
            except KeyboardInterrupt:
                log.info("Keyboard interrupt :(")
                service.reset()
                exit()
            except:
                service.reset()
                raise
    except:
        log.exception('Unknow Error')
        raise
