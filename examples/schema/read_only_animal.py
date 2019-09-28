import graphene
from graphene import Node
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)
from graphene_elastic.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
)
from graphene_elastic.constants import (
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_IN,
)

from search_index.documents import ReadOnlyAnimal as ReadOnlyAnimalDocument


__all__ = (
    'ReadOnlyAnimal',
    'Query',
    'schema',
)


class ReadOnlyAnimal(ElasticsearchObjectType):
    """Read-only animal."""

    class Meta:

        document = ReadOnlyAnimalDocument
        interfaces = (Node,)
        filter_backends = [
            # FilteringFilterBackend,
            SearchFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]
        filter_fields = {
            'id': {
                'field': 'id',
                'default_lookup': LOOKUP_FILTER_TERM,
            },
            'action': {
                'field': 'action.raw',
                'default_lookup': LOOKUP_FILTER_TERM,
            },
            'entity': {
                'field': 'entity.raw',
                'default_lookup': LOOKUP_FILTER_TERM,
            },
            'app': {
                'field': 'app.raw',
                'default_lookup': LOOKUP_FILTER_TERM,
            },
        }
        search_fields = {
            'action': None,
            'entity': None,
        }
        ordering_fields = {
            'id': 'id',
            'publish_date': 'publish_date',
            'action': 'action.raw',
            'entity': 'entity.raw',
        }

        ordering_defaults = (
            'id',
            'publish_date'
        )


class Query(graphene.ObjectType):
    """Animal query."""

    read_only_animals = ElasticsearchConnectionField(ReadOnlyAnimal)


schema = graphene.Schema(
    query=Query
)
