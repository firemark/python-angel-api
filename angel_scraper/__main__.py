from .web import app
import argparse
from requests.exceptions import HTTPError
from .scraper import get

parser = argparse.ArgumentParser()
parser.add_argument("first", help="first id", type=int)
parser.add_argument("last", help="last id", type=int)


if __name__ == '__main__':
    args = parser.parse_args()

    for i in range(args.first, args.last + 1):
        try:
            resp = get("startups", i)
            if resp["hidden"] is False:
                print("id:", i, "name:", resp["name"])
            else:
                print("id:", i, "hidden office")
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e
            else:
                print("id:", i, "not found")

    #app.run()