from .web import app
from .api import get_startup
from .utils import load_config
from .db import Database
from . import config

import argparse
from itertools import count
from requests.exceptions import HTTPError


parser = argparse.ArgumentParser()
parser.add_argument("config", type=str, help="path to config file",
                    default="config.ini", nargs="?")
parser.add_argument("--start", type=int, default=1)

if __name__ == '__main__':
    args = parser.parse_args()

    try:
        load_config(args.config)
    except FileNotFoundError as e:
        print("Config %s not found!" % e.args[0])
        exit()

    watchdog_counter = 0

    while True:
        for i in count(args.start):
            try:
                watchdog_counter += 1
                if watchdog_counter > config.watchdog_reset:
                    break
                resp = get_startup(i)

            except HTTPError as e:
                http_resp = e.response
                print("!!!", "id:", i ,"http_code", http_resp.status_code)
                print(http_resp.json())
            else:
                if not resp:
                    print("id:", i, "not found")
                elif resp["hidden"]:
                    print("id:", i, "hidden office")
                    #pprint(resp)
                else:
                    watchdog_counter = 0
                    Database.index(id=resp["id"], data=resp)
                    print("id:", i, "name:", resp["name"])


    #app.run()