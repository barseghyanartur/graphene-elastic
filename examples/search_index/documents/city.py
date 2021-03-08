import datetime
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
from .settings import ADDRESS_CITY_DOCUMENT_NAME, ELASTICSEARCH_CONNECTION

try:
    from elasticsearch import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

__all__ = (
    'City',
)

connections.create_connection(**ELASTICSEARCH_CONNECTION)


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class City(Document):

    name = Text(fields={'raw': Keyword()})
    country = Nested(
        properties={
            'name': Text(
                analyzer=html_strip,
                fields={
                    'raw': Keyword(),
                    # 'suggest': Completion(),
                }
            )
        }
    )

    class Index:
        name = ADDRESS_CITY_DOCUMENT_NAME
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1,
            'blocks': {'read_only_allow_delete': None},
        }


try:
    # Create the mappings in Elasticsearch
    City.init()
except Exception as err:
    logger.error(err)
