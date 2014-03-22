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
    def index(cls, id, data, doc_type="data"):
        return cls.get_db().index(index=config.index_name,
                                  doc_type=doc_type,
                                  refresh=True,
                                  id=id, body=data)

    @classmethod
    def exists(cls, id, doc_type="data"):
        return cls.get_db().exists(index=config.index_name,
                                   id=id, doc_type=doc_type)