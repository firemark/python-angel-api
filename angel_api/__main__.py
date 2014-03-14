from .web import app
from .api import get_startup

import argparse

from json import dumps


parser = argparse.ArgumentParser()
parser.add_argument("first", help="first id", type=int)
parser.add_argument("last", help="last id", type=int, default=None, nargs='?')

if __name__ == '__main__':
    args = parser.parse_args()

    if args.last is None:
        print(dumps(
            get_startup(args.first),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ))
    else:
        for i in range(args.first, args.last + 1):
            resp = get_startup(i, with_founders=False)
            if not resp:
                print("id:", i, "not found")
            elif not resp["hidden"]:
                print("id:", i, "name:", resp["name"])
                #pprint(resp)
            else:
                print("id:", i, "hidden office")

    #app.run()