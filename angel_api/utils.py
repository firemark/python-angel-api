from . import config

from configparser import ConfigParser
from logging import handlers
from sys import stderr
import logging


log = logging.getLogger("angelo-api")

def yes_or_no(obj):
    if obj == "yes":
        return True
    elif obj == "no":
        return False

    raise TypeError(obj)

def load_config_from_file(file):
    cfg = ConfigParser()

    if not cfg.read(file):
        raise FileNotFoundError(file)

    load_config(cfg)

def load_config(cfg):

    config.elastic_hosts = [
        host.strip() for host
        in cfg['elasticsearch']["hosts"].split(",")
    ]

    app = cfg['app']

    config.brute_force = yes_or_no(app["brute_force"])
    config.watchdog_reset = int(app.get('watchdog_reset', 20))
    config.requests_per_hour = int(app.get("requests_per_hour", 1000))

    cfg_log = cfg['logging']

    log_filename = cfg_log.get('filename')

    if log_filename:
        if yes_or_no(cfg_log["time_rotating"]):
            handler = handlers.TimedRotatingFileHandler(
                filename=log_filename,
                when='D'
            )
        else:
            handler = logging.StreamHandler(log_filename)
    else:
        handler = logging.StreamHandler(stderr)

    log_level = getattr(logging, cfg_log.get("level", "INFO").upper())
    handler.setLevel(log_level)
    handler.setFormatter(
        logging.Formatter(
            cfg_log.get('format', '%(asctime)s %(levelname)s:%(message)s')
        )
    )

    log.addHandler(handler)
    log.setLevel(log_level)

    account = cfg['account']
    config.has_account = yes_or_no(account["has_account"])

    if config.has_account:
        config.client_id = account["client_id"]
        config.client_secret = account["client_secret"]
        config.access_token = account.get("access_token")
    else:
        config.client_id = ""
        config.client_secret = ""
        config.access_token = None

    web = cfg["web"]

    config.host = web["host"]
    config.port = int(web["port"])
