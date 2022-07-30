from anysearch.search_dsl import (
    connections,
    analyzer,
    Integer,
    Boolean,
    Completion,
    Date,
    Document,
    InnerDoc,
    Keyword,
    Nested,
    Object,
    Text,
)
from .read_only import ReadOnlyDocument
from .settings import FARM_ANIMAL_DOCUMENT_NAME, ELASTICSEARCH_CONNECTION

try:
    from elasticsearch import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

__all__ = (
    'Animal',
    'ReadOnlyAnimal',
)

connections.create_connection(**ELASTICSEARCH_CONNECTION)


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

html_strip_preserve_case = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["stop", "snowball"],
    char_filter=["html_strip"]
)


class Animal(Document):

    scope = Object(
        properties={
            'farm_id': Text(),
            'holding_id': Text(),
        }
    )
    action = Text(analyzer=html_strip, fields={'raw': Keyword()})
    entity = Text(analyzer=html_strip, fields={'raw': Keyword()})
    # This is not internal ID of the Elasticsearch
    id = Keyword()
    app = Text(analyzer=html_strip_preserve_case, fields={'raw': Keyword()})
    message_id = Text()
    publish_date = Date()
    data = Object(
        properties={
            'id': Integer(),
            'genetic': Object(
                properties={
                    'id': Integer(),
                    'name': Text(),
                }
            ),
            'animal_type': Object(
                properties={
                    'id': Integer(),
                    'name': Text(),
                    'gender': Object(
                        properties={
                            'id': Integer(),
                            'name': Text(),
                        }
                    ),
                }
            ),
        }
    )
    uuid = Text()

    class Index:
        name = FARM_ANIMAL_DOCUMENT_NAME
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1,
            'blocks': {'read_only_allow_delete': None},
        }


class ReadOnlyAnimal(ReadOnlyDocument):

    scope = Object(
        properties={
            'farm_id': Text(),
            'holding_id': Text(),
        }
    )
    action = Text(analyzer=html_strip, fields={'raw': Keyword()})
    entity = Text(analyzer=html_strip, fields={'raw': Keyword()})
    # This is not internal ID of the Elasticsearch
    id = Keyword()
    app = Text(analyzer=html_strip_preserve_case, fields={'raw': Keyword()})
    message_id = Text()
    publish_date = Date()
    data = Object(
        properties={
            'id': Integer(),
            'genetic': Object(
                properties={
                    'id': Integer(),
                    'name': Text(),
                }
            ),
            'animal_type': Object(
                properties={
                    'id': Integer(),
                    'name': Text(),
                    'gender': Object(
                        properties={
                            'id': Integer(),
                            'name': Text(),
                        }
                    ),
                }
            ),
        }
    )
    uuid = Text()

    class Index:
        name = FARM_ANIMAL_DOCUMENT_NAME
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1,
            'blocks': {'read_only_allow_delete': None},
        }


try:
    # Create the mappings in Elasticsearch
    Animal.init()
except Exception as err:
    logger.error(err)
