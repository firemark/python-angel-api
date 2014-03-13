from .config import ANGEL_URL
import requests


def get(*args, params=None):
    str_args = (str(arg) for arg in args)
    resp = requests.get(ANGEL_URL + "/".join(str_args), params=params)

    resp.raise_for_status()
    return resp.json()

#GET https://api.angel.co/1/users/155?test=test
#get("users", 155, params=dict(test="test"))