from . import config


from requests.exceptions import HTTPError
from threading import Event
import requests
import logging

log = logging.getLogger("angelo-api")

account_event = Event()
code = None

def get(*args, params=None):
    """
    GET https://api.angel.co/1/users/155?test=test
    get("users", 155, params={"test":"test"})
    """
    str_args = (str(arg) for arg in args)
    params = params or {}
    if config.access_token:
        params["access_token"] = config.access_token
    resp = requests.get(config.ANGEL_URL + "/".join(str_args), params=params)
    log.debug("request url %s", resp.url)

    resp.raise_for_status()
    return resp.json()

def get_access_token():

    print(
        "Link: https://angel.co/api/oauth/authorize?client_id={}"
        "&response_type=code".format(config.client_id)
    )
    print("waiting for a request…")

    account_event.wait()

    resp = requests.post("https://angel.co/api/oauth/token", params={
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "code": code,
        "grant_type": "authorization_code"
    })

    resp.raise_for_status()
    access_token = resp.json()["access_token"]
    print("Access token is: ", access_token)

    config.access_token = access_token

def get_or_none(*args, params=None):
    try:
        return get(*args, params=params)
    except HTTPError as e:
        if e.response.status_code != 404:
            raise e
        return None

def get_founders_from_roles(roles, with_details=True):
    ids = (r["id"] for r in roles if r["role"] == "founder")

    params = {"include_details": "investor"} if with_details else None
    users = (get_or_none("users", user_id, params=params) for user_id in ids)

    return [user for user in users if user is not None]

def get_startup(startup_id, with_founders=True, with_details=True):

    startup = get_or_none("startups", startup_id)
    if startup and not startup["hidden"]:
        roles = get("startups", startup_id, "roles")["startup_roles"]
        if with_founders:
            startup["founders"] = get_founders_from_roles(
                roles,
                with_details=with_details
            )

    return startup
