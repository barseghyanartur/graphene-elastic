from graphene import Node
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
    # SuggestFilterBackend,
    SimpleQueryStringBackend,
    QueryStringBackend,
)

from graphene_elastic.constants import (
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_CONTAINS,
    SUGGESTER_COMPLETION,
)


from search_index.documents import Post as PostDocument

# from ..custom_backends import CustomFilterBackend
from ..meta.post import AbstractPostDocumentMeta

__all__ = (
    'Post',
    'PostSuggest',
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


class PostSuggest(ElasticsearchObjectType):

    class Meta:

        document = PostDocument
        interfaces = (Node,)
        filter_backends = [
            # FilteringFilterBackend,
            # PostFilterFilteringBackend,
            # SearchFilterBackend,
            # HighlightFilterBackend,
            # SourceFilterBackend,
            # FacetedSearchFilterBackend,
            # # CustomFilterBackend,
            # ScoreFilterBackend,
            # OrderingFilterBackend,
            # DefaultOrderingFilterBackend,
            # SuggestFilterBackend,
        ]

        # Suggester fields
        suggest_fields = {
            'title_suggest': {
                'field': 'title.suggest',
                'default_suggester': SUGGESTER_COMPLETION,
                'options': {
                    'size': 20,
                    'skip_duplicates': True,
                },
            },
            'title_suggest_context': {
                'field': 'title.suggest_context',
                'suggesters': [
                    SUGGESTER_COMPLETION,
                ],
                'default_suggester': SUGGESTER_COMPLETION,
                # We want to be able to filter the completion filter
                # results on the following params: tag, state and publisher.
                # We also want to provide the size value.
                # See the "https://www.elastic.co/guide/en/elasticsearch/
                # reference/6.1/suggester-context.html" for the reference.
                'completion_options': {
                    'category_filters': {
                        'title_tag': 'tag',
                        'title_state': 'state',
                        'title_publisher': 'publisher',
                    },
                },
                'options': {
                    'size': 20,
                },
            },
            'publisher_suggest': 'publisher.suggest',
            'tag_suggest': 'tags.suggest',
        }


class PostForUser(ElasticsearchObjectType):

    class Meta(AbstractPostDocumentMeta):
        pass
