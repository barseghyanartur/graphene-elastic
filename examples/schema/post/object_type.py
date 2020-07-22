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
)

from search_index.documents import Post as PostDocument
# from ..custom_backends import CustomFilterBackend
from ..meta.post import AbstractPostDocumentMeta
__all__ = (
    'Post',
)


class Post(ElasticsearchObjectType):
    """PostDocument object type."""

    class Meta(AbstractPostDocumentMeta):
        document = PostDocument
        filter_backends = [
            FilteringFilterBackend,
            PostFilterFilteringBackend,
            SearchFilterBackend,
            HighlightFilterBackend,
            SourceFilterBackend,
            FacetedSearchFilterBackend,
            # CustomFilterBackend,
            ScoreFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]
