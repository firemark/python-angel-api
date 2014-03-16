from configparser import ConfigParser
from . import config

def yes_or_no(obj):
    if obj == "yes":
        return True
    elif obj == "no":
        return False

    raise TypeError(obj)

def load_config(file):
    cfg = ConfigParser()
    if not cfg.read(file):
        raise FileNotFoundError(file)

    config.elastic_hosts = [
        host.strip() for host
        in cfg['elasticsearch']["hosts"].split(",")
    ]
    config.brute_force = yes_or_no(cfg['app']["brute_force"])
    config.watchdog_reset = int(cfg['app'].get('watchdog_reset', 20))


    account = cfg['account']
    config.has_account = yes_or_no(account["has_account"])

    if config.has_account:
        config.client_id = account["client_id"]
        config.client_secret = account["client_secret"]
    else:
        config.client_id = ""
        config.client_secret = ""