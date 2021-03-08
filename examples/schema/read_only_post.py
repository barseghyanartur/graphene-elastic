import graphene
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)
from graphene_elastic.filter_backends import (
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
    OrderingFilterBackend,
    PostFilterFilteringBackend,
    DefaultOrderingFilterBackend,
    HighlightFilterBackend,
    SourceFilterBackend,
)

from search_index.documents import ReadOnlyPost as ReadOnlyPostDocument
from .meta.post import AbstractPostDocumentMeta

__all__ = (
    'ReadOnlyPost',
    'Query',
    'schema',
)


class ReadOnlyPost(ElasticsearchObjectType):
    """Read only PostDocument object type."""

    class Meta(AbstractPostDocumentMeta):
        document = ReadOnlyPostDocument
        filter_backends = [
            FilteringFilterBackend,
            PostFilterFilteringBackend,
            CompoundSearchFilterBackend,
            HighlightFilterBackend,
            SourceFilterBackend,
            FacetedSearchFilterBackend,
            # CustomFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]


class Query(graphene.ObjectType):
    """ReadOnlyPostDocument query."""

    all_read_only_post_documents = ElasticsearchConnectionField(ReadOnlyPost)


schema = graphene.Schema(
    query=Query
)
