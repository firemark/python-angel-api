from .web import app
from .api import get_startup
from .utils import load_config

import argparse
from itertools import count


parser = argparse.ArgumentParser()
parser.add_argument("config", type=str, help="path to config file",
                    default="config.ini", nargs="?")

if __name__ == '__main__':
    args = parser.parse_args()

    try:
        load_config(args.config)
    except FileNotFoundError as e:
        print("Config %s not found!" % e.args[0])
        exit()

    while True:
        for i in count(1):
            resp = get_startup(i, with_founders=False)
            if not resp:
                print("id:", i, "not found")
            elif not resp["hidden"]:
                print("id:", i, "name:", resp["name"])
                #pprint(resp)
            else:
                print("id:", i, "hidden office")

    #app.run()