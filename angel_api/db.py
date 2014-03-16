from . import config

from elasticsearch import Elasticsearch


class Database(object):

    _db = None

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls._db = Elasticsearch(config.elastic_hosts)
        return cls._db

    @classmethod
    def index(cls, id, data):
        return cls.get_db().index(index="startups",
                                  doc_type="data",
                                  id=id, body=data)

