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
    CompoundSearchFilterBackend,
)

from search_index.documents import Animal as AnimalDocument
from .meta.animal import AbstractAnimalDocumentMeta

__all__ = (
    'Animal',
    'Query',
    'schema',
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
        ]

    # class Meta:
    #
    #     document = AnimalDocument
    #     filter_backends = [
    #         FilteringFilterBackend,
    #         PostFilterFilteringBackend,
    #         # SearchFilterBackend,
    #         CompoundSearchFilterBackend,
    #         OrderingFilterBackend,
    #         DefaultOrderingFilterBackend,
    #     ]
    #     interfaces = (Node,)
    #
    #     # For filter backend
    #     filter_fields = {
    #         'id': {
    #             'field': 'id',
    #             'default_lookup': LOOKUP_FILTER_TERM,
    #         },
    #         'action': {
    #             'field': 'action.raw',
    #             'default_lookup': LOOKUP_FILTER_TERM,
    #         },
    #         'entity': {
    #             'field': 'entity.raw',
    #             'default_lookup': LOOKUP_FILTER_TERM,
    #         },
    #         'app': {
    #             'field': 'app.raw',
    #             'default_lookup': LOOKUP_FILTER_TERM,
    #         },
    #     }
    #
    #     # For search backend
    #     search_fields = {
    #         'action': None,
    #         'entity': None,
    #     }
    #
    #     # For ordering backend
    #     ordering_fields = {
    #         'id': 'id',
    #         'publish_date': 'publish_date',
    #         'action': 'action.raw',
    #         'entity': 'entity.raw',
    #     }
    #
    #     # For default ordering backend
    #     ordering_defaults = (
    #         'id',
    #         'publish_date'
    #     )
    #
    #     # For filter backend
    #     post_filter_fields = {
    #         'id': {
    #             'field': 'id',
    #             'default_lookup': LOOKUP_FILTER_TERM,
    #         },
    #         'action': {
    #             'field': 'action.raw',
    #             'default_lookup': LOOKUP_FILTER_TERM,
    #         },
    #         'entity': {
    #             'field': 'entity.raw',
    #             'default_lookup': LOOKUP_FILTER_TERM,
    #         },
    #         'app': {
    #             'field': 'app.raw',
    #             'default_lookup': LOOKUP_FILTER_TERM,
    #         },
    #     }


class Query(graphene.ObjectType):
    """Animal query."""

    animals = ElasticsearchConnectionField(Animal)


schema = graphene.Schema(
    query=Query
)
