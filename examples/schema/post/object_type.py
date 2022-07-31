from graphene_elastic import ElasticsearchObjectType
from graphene_elastic.filter_backends import (
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    SearchFilterBackend,
    OrderingFilterBackend,
    PostFilterFilteringBackend,
    DefaultOrderingFilterBackend,
    HighlightFilterBackend,
    SourceFilterBackend,
    ScoreFilterBackend,
    SimpleQueryStringBackend,
    QueryStringBackend,
)

from search_index.documents import Post as PostDocument

# from ..custom_backends import CustomFilterBackend
from ..meta.post import AbstractPostDocumentMeta

__all__ = (
    "Post",
    "AlternativePost",
    "PostForUser",
)


class Post(ElasticsearchObjectType):
    """PostDocument object type."""

    class Meta(AbstractPostDocumentMeta):
        pass


class AlternativePost(ElasticsearchObjectType):
    class Meta(AbstractPostDocumentMeta):
        # For `OrderingFilterBackend` backend
        ordering_fields = {
            # The dictionary key (in this case `created_at`) is the name of
            # the corresponding GraphQL query argument. The dictionary
            # value (in this case `created_at`) is the field name in the
            # Elasticsearch document (`PostDocument`).
            "created_at",
            # The dictionary key (in this case `num_views`) is the name of
            # the corresponding GraphQL query argument. The dictionary
            # value (in this case `num_views`) is the field name in the
            # Elasticsearch document (`PostDocument`).
            "num_views",
        }


class PostForUser(ElasticsearchObjectType):

    class Meta(AbstractPostDocumentMeta):
        pass
