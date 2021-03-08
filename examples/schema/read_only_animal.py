import graphene
from graphene import Node
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)
from graphene_elastic.filter_backends import (
    FilteringFilterBackend,
    PostFilterFilteringBackend,
    SearchFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    CompoundSearchFilterBackend,
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
from .meta.animal import AbstractAnimalDocumentMeta

__all__ = (
    'ReadOnlyAnimal',
    'Query',
    'schema',
)


class ReadOnlyAnimal(ElasticsearchObjectType):
    """Read-only animal."""

    class Meta(AbstractAnimalDocumentMeta):

        document = ReadOnlyAnimalDocument


class Query(graphene.ObjectType):
    """Animal query."""

    read_only_animals = ElasticsearchConnectionField(ReadOnlyAnimal)


schema = graphene.Schema(
    query=Query
)
