python-angelo-scraper
=====================

installing
----

    virtualenv -p python3.3 venv
    source venv/bin/activate
    python setup.py install

or

    python setup.py develop

usage
----

    source venv/bin/activate
    python -m angel_api 1 50 # returns startups from id 1 to 50
    python -m angel_api 50 # return big json with id = 50