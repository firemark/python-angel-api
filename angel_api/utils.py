from . import config

from configparser import ConfigParser
from logging import handlers
from sys import stderr, stdout
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

    es = cfg['elasticsearch']

    config.elastic_hosts = [
        host.strip() for host
        in es["hosts"].split(",")
    ]

    config.index_name = es["index_name"]
    config.index_config_name = es.get("index_config_name", "config")

    app = cfg['app']

    config.brute_force = yes_or_no(app["brute_force"])
    config.watchdog_reset = int(app.get('watchdog_reset', 20))
    config.requests_per_hour = int(app.get("requests_per_hour", 1000))
    config.round_trip = yes_or_no(app.get("round_trip", "no"))
    config.delay_connection = int(app.get("delay_connection", 60))

    cfg_log = cfg['logging']

    log_filename = cfg_log.get('filename')

    if log_filename and log_filename not in ['stderr', 'stdout']:
        if yes_or_no(cfg_log["time_rotating"]):
            handler = handlers.TimedRotatingFileHandler(
                filename=log_filename,
                when='D'
            )
        else:
            handler = logging.StreamHandler(log_filename)
    else:
        stream = stdout if log_filename == "stdout" else stderr
        handler = logging.StreamHandler(stream)

    log_level = getattr(logging, cfg_log.get("level", "INFO").upper())

    logging.getLogger('elasticsearch').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)

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
