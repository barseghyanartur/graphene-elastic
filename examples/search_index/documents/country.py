from anysearch.search_dsl import (
    analyzer,
    Boolean,
    connections,
    Completion,
    Date,
    Document,
    InnerDoc,
    Keyword,
    Nested,
    Text,
)
from .settings import ADDRESS_COUNTRY_DOCUMENT_NAME, ELASTICSEARCH_CONNECTION

try:
    from elasticsearch import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

__all__ = (
    'Country',
)

connections.create_connection(**ELASTICSEARCH_CONNECTION)


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)


class Country(Document):
    name = Text(fields={'raw': Keyword()})

    class Index:
        name = ADDRESS_COUNTRY_DOCUMENT_NAME
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1,
            'blocks': {'read_only_allow_delete': None},
        }


try:
    # Create the mappings in Elasticsearch
    Country.init()
except Exception as err:
    logger.error(err)
