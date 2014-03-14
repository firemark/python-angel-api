from .config import ANGEL_URL
from requests.exceptions import HTTPError
import requests


def get(*args, params=None):
    """
    GET https://api.angel.co/1/users/155?test=test
    get("users", 155, params={"test":"test"})
    """
    str_args = (str(arg) for arg in args)
    resp = requests.get(ANGEL_URL + "/".join(str_args), params=params)

    resp.raise_for_status()
    return resp.json()


def get_or_none(*args, params=None):
    try:
        return get(*args, params=params)
    except HTTPError as e:
        if e.response.status_code != 404:
            raise e
        return None

def get_founders_from_roles(roles, with_details=True):
    ids = (r["id"] for r in roles if r["role"] == "founder")

    #params = {"include_details": "investor"} if with_details else None
    users = (get_or_none(user_id) for user_id in ids)

    return [user for user in users if user is not None]

def get_startup(startup_id, with_founders=True, with_details=True):

    startup = get_or_none("startups", startup_id)
    if startup and not startup["hidden"]:
        roles = get("startups", startup_id, "roles")["startup_roles"]
        if with_founders:
            startup["roles"] = roles
            startup["founders"] = get_founders_from_roles(roles, with_details=with_details)

    return startup
