from .web import app
from .utils import load_config_from_file
from .run import run
from . import config

import argparse
from threading import Thread


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=str, help="path to config file",
                        default="config.ini", nargs="?")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--continuous", action='store_const',
                        const=True, default=False)

    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()


    try:
        load_config_from_file(args.config)
    except FileNotFoundError as e:
        print("Config %s not found!" % e.args[0])
    else:
        api_thread = Thread(target=run, args=(args.start, args.continuous))
        api_thread.start()
        if config.has_account and not config.access_token:
            app.run(config.host, config.port)