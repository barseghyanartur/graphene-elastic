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
    SimpleQueryStringBackend,
)
from graphene_elastic.constants import (
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_IN,
)

from search_index.documents import Animal as AnimalDocument


__all__ = (
    "Animal",
    "Query",
    "schema",
)


class Animal(ElasticsearchObjectType):
    """Animal."""

    class Meta:

        document = AnimalDocument
        interfaces = (Node,)
        filter_backends = [
            FilteringFilterBackend,
            PostFilterFilteringBackend,
            SearchFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
            SimpleQueryStringBackend,
        ]

        # For filter backend
        filter_fields = {
            "id": {
                "field": "id",
                "default_lookup": LOOKUP_FILTER_TERM,
            },
            "action": {
                "field": "action.raw",
                "default_lookup": LOOKUP_FILTER_TERM,
            },
            "entity": {
                "field": "entity.raw",
                "default_lookup": LOOKUP_FILTER_TERM,
            },
            "app": {
                "field": "app.raw",
                "default_lookup": LOOKUP_FILTER_TERM,
            },
        }

        # For search backend
        search_fields = {
            "action": None,
            "entity": None,
        }

        # For simple query backend
        simple_query_string_options = {"fields": ["action", "entity"]}

        # For ordering backend
        ordering_fields = {
            "id": "id",
            "publish_date": "publish_date",
            "action": "action.raw",
            "entity": "entity.raw",
        }

        # For default ordering backend
        ordering_defaults = ("id", "publish_date")

        # For filter backend
        post_filter_fields = {
            "id": {
                "field": "id",
                "default_lookup": LOOKUP_FILTER_TERM,
            },
            "action": {
                "field": "action.raw",
                "default_lookup": LOOKUP_FILTER_TERM,
            },
            "entity": {
                "field": "entity.raw",
                "default_lookup": LOOKUP_FILTER_TERM,
            },
            "app": {
                "field": "app.raw",
                "default_lookup": LOOKUP_FILTER_TERM,
            },
        }


class Query(graphene.ObjectType):
    """Animal query."""

    animals = ElasticsearchConnectionField(Animal)


schema = graphene.Schema(query=Query)
