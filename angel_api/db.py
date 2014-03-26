from . import config

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError



class Database(object):

    _db = None

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls._db = Elasticsearch(config.elastic_hosts)
        return cls._db

    @classmethod
    def index(cls, id, data, doc_type="data", index=""):
        index = index or config.index_name
        return cls.get_db().index(index=index,
                                  doc_type=doc_type,
                                  refresh=True,
                                  id=id, body=data)

    @classmethod
    def exists(cls, id, doc_type="data", index=""):
        index = index or config.index_name
        return cls.get_db().exists(index=index,
                                   id=id, doc_type=doc_type)

    @classmethod
    def get(cls, id, doc_type="data", index=""):
        index = index or config.index_name

        try:
            resp = cls.get_db().get(index=index, doc_type=doc_type,
                                    id=id)
        except NotFoundError:
            return None
        else:
            return resp["_source"]


    @classmethod
    def search(cls, query, doc_type="data", index=""):
        index = index or config.index_name
        body = {"query": {"match": query}}
        resp = cls.get_db().search(index=index, doc_type=doc_type,
                                   body=body, fields="", size=1)

        try:
            return resp["hits"]["hits"][0]["_id"]
        except IndexError:
            return None