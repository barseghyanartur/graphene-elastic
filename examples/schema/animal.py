import graphene
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
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


class Query(graphene.ObjectType):
    """Animal query."""

    animals = ElasticsearchConnectionField(Animal)


schema = graphene.Schema(query=Query)
