import graphene
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
    SimpleQueryStringBackend,
    # CompoundSearchFilterBackend,
)

from search_index.documents import Animal as AnimalDocument
from .meta.animal import AbstractAnimalDocumentMeta

__all__ = (
    "Animal",
    "Query",
    "schema",
)


class Animal(ElasticsearchObjectType):
    """Animal."""

    class Meta(AbstractAnimalDocumentMeta):

        document = AnimalDocument
        filter_backends = [
            FilteringFilterBackend,
            PostFilterFilteringBackend,
            SearchFilterBackend,
            # CompoundSearchFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
            SimpleQueryStringBackend,
        ]


class Query(graphene.ObjectType):
    """Animal query."""

    animals = ElasticsearchConnectionField(Animal)


schema = graphene.Schema(query=Query)
