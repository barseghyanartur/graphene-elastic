import datetime
from elasticsearch import logger
from elasticsearch_dsl import connections
from elasticsearch_dsl import (
    analyzer,
    Boolean,
    Completion,
    Date,
    Document,
    InnerDoc,
    Keyword,
    Nested,
    Text,
)

__all__ = (
    'User',
)

connections.create_connection(hosts=['localhost'], timeout=20)


html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class User(Document):
    first_name = Text()
    last_name = Text()
    email = Text()
    created_at = Date()

    class Index:
        name = 'site_user'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1,
            'blocks': {'read_only_allow_delete': None},
        }

    def save(self, ** kwargs):
        self.created_at = datetime.datetime.now()
        return super().save(** kwargs)


try:
    # Create the mappings in Elasticsearch
    User.init()
except Exception as err:
    logger.error(err)
