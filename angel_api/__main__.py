from .web import app
from .api import get_startup
from .utils import load_config_from_file
from .db import Database
from . import config

import argparse
import logging
from itertools import count
from requests.exceptions import HTTPError
from threading import Thread, Lock

log = logging.getLogger("angelo-api")


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=str, help="path to config file",
                        default="config.ini", nargs="?")
    parser.add_argument("--start", type=int, default=1)

    return parser



def run(start=1):
    watchdog_counter = 0

    log.info("Start.")

    while True:
        for i in count(args.start):
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


account_lock = Lock()

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    try:
        load_config_from_file(args.config)
    except FileNotFoundError as e:
        print("Config %s not found!" % e.args[0])
    else:
        run(args.start)



    #app.run()