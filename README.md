python-angel-api
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
    python -m angel_api
    python -m angel_api config.ini
    python -m angel_api congig.ini --start 100
    python -m angel_api --continuous

requirements
----
    python3.3 (in python2.7 not tested)
    virtualenv (in ubuntu package python-virtualenv)
    ElasticSearch server
