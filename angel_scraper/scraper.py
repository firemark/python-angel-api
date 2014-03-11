from .config import ANGEL_URL
import requests


def get(*args):
    str_args = (str(arg) for arg in args)
    resp = requests.get(ANGEL_URL + "/".join(str_args))

    if resp.status_code == 200:
        return resp.json()
    else:
        #todo
        return {}

#GET https://api.angel.co/1/users/155
#get("users", 155)