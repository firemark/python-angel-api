
from . import config
from importlib import import_module

from time import sleep
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError as RequestConnectionError
from elasticsearch.exceptions import (RequestError, NotFoundError,
                                      ConflictError, TransportError)

import logging

log = logging.getLogger("angelo-api")


def get_class(module_str):
    *module_name, class_name = module_str.split(".")
    module = import_module(".".join(module_name))
    return getattr(module, class_name)

def run(start=1, continuous=False):

    service_class = get_class(config.service_module)
    db_class = get_class(config.db_module)
    api_class = get_class(config.rest_api_module)

    try:
        log.info("Start.")
        while True:
            try:
                service = service_class(
                            api_class=api_class,
                            db_class=db_class,
                            start=start,
                            continuous=continuous)
            except TransportError as e:
                log.error("ES Critical Error (while creating service: %s)"
                          ", waiting %d seconds", e,
                          config.delay_connection)
                sleep(config.delay_connection)
            else:
                break

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
