from elasticsearch_dsl import DateHistogramFacet, RangeFacet
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
    SimpleQueryStringBackend,
    QueryStringBackend,
)
from graphene_elastic.constants import (
    ALL_LOOKUP_FILTERS_AND_QUERIES, LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_CONTAINS,
)
from graphene_elastic.filter_backends.filtering.nested import NestedFilteringFilterBackend

from search_index.documents import Post as PostDocument

# from ..custom_backends import CustomFilterBackend

__all__ = (
    "Post",
    "AlternativePost",
    "PostForUser",
)


class BasePostMeta:

    document = PostDocument
    interfaces = (Node,)
    filter_backends = [
        FilteringFilterBackend,
        PostFilterFilteringBackend,
        SearchFilterBackend,
        HighlightFilterBackend,
        SourceFilterBackend,
        FacetedSearchFilterBackend,
        NestedFilteringFilterBackend,
        # CustomFilterBackend,
        ScoreFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SimpleQueryStringBackend,
        QueryStringBackend,
    ]
    # For `FilteringFilterBackend` backend
    filter_fields = {
        # 'id': '_id',
        # The dictionary key (in this case `title`) is the name of
        # the corresponding GraphQL query argument. The dictionary
        # value could be simple or complex structure (in this case
        # complex). The `field` key points to the `title.raw`, which
        # is the field name in the Elasticsearch document
        # (`PostDocument`). Since `lookups` key is provided, number
        # of lookups is limited to the given set, while term is the
        # default lookup (as specified in `default_lookup`).
        "title": {
            "field": "title.raw",  # Field name in the Elastic doc
            # Available lookups
            "lookups": [
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_TERM,
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_CONTAINS,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_QUERY_IN,
            ],
            # Default lookup
            "default_lookup": LOOKUP_FILTER_TERM,
        },
        # The dictionary key (in this case `category`) is the name of
        # the corresponding GraphQL query argument. Since no lookups
        # or default_lookup is provided, defaults are used (all lookups
        # available, term is the default lookup). The dictionary value
        # (in this case `category.raw`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "category": "category.raw",
        # The dictionary key (in this case `tags`) is the name of
        # the corresponding GraphQL query argument. Since no lookups
        # or default_lookup is provided, defaults are used (all lookups
        # available, term is the default lookup). The dictionary value
        # (in this case `tags.raw`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "tags": "tags.raw",
        # The dictionary key (in this case `num_views`) is the name of
        # the corresponding GraphQL query argument. Since no lookups
        # or default_lookup is provided, defaults are used (all lookups
        # available, term is the default lookup). The dictionary value
        # (in this case `num_views`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "num_views": "num_views",
        # The dictionary key (in this case `created_at`) is the name of
        # the corresponding GraphQL query argument. Since no lookups
        # or default_lookup is provided, defaults are used (all lookups
        # available, term is the default lookup). The dictionary value
        # (in this case `created_at`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "created_at": "created_at",
        "i_do_not_exist": "i_do_not_exist",
    }

    nested_filter_fields = {
        "comments": {
            "author": {
                "lookups": ALL_LOOKUP_FILTERS_AND_QUERIES
            },
            "content": {
                "lookups": [
                    LOOKUP_FILTER_TERM,
                    LOOKUP_FILTER_TERMS,
                    LOOKUP_QUERY_CONTAINS
                ]
            }
        }
    }

    # For `SearchFilterBackend` backend
    search_fields = {
        "title": {"field": "title", "boost": 4},
        "content": {"boost": 2},
        "category": None,
    }

    simple_query_string_options = {
        "fields": ["title^2", "content", "category"],
        "boost": 2,
    }

    query_string_options = {
        "fields": ["title^2", "content", "category"],
        "boost": 2,
    }

    # For `OrderingFilterBackend` backend
    ordering_fields = {
        # The dictionary key (in this case `title`) is the name of
        # the corresponding GraphQL query argument. The dictionary
        # value (in this case `title.raw`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "title": "title.raw",
        # The dictionary key (in this case `created_at`) is the name of
        # the corresponding GraphQL query argument. The dictionary
        # value (in this case `created_at`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "created_at": "created_at",
        # The dictionary key (in this case `num_views`) is the name of
        # the corresponding GraphQL query argument. The dictionary
        # value (in this case `num_views`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "num_views": "num_views",
        # Add ordering by score. The dictionary key (in this case `score`)
        # is the name of the corresponding GraphQL query argument (how you
        # want it to be). The dictionary value (in this case `_score`) is
        # the reserved Elasticsearch name.
        "score": "_score",
    }

    # For `DefaultOrderingFilterBackend` backend
    ordering_defaults = (
        "-num_views",  # Field name in the Elasticsearch document
        "title.raw",  # Field name in the Elasticsearch document
    )

    # For `HighlightFilterBackend` backend
    highlight_fields = {
        "title": {
            "enabled": True,
            "options": {
                "pre_tags": ["<b>"],
                "post_tags": ["</b>"],
            },
        },
        "content": {
            "options": {"fragment_size": 50, "number_of_fragments": 3}
        },
        "category": {},
    }

    # For `FacetedSearchFilterBackend` backend
    faceted_search_fields = {
        "category": "category.raw",
        "category_global": {
            "field": "category.raw",
            # 'enabled': True,
            "global": True,
        },
        "tags": {
            "field": "tags.raw",
            "enabled": True,
            "global": True,
        },
        "created_at": {
            "field": "created_at",
            "facet": DateHistogramFacet,
            "options": {
                "interval": "year",
            },
        },
        "num_views_count": {
            "field": "num_views",
            "facet": RangeFacet,
            "options": {
                "ranges": [
                    ("<10", (None, 10)),
                    ("11-20", (11, 20)),
                    ("20-50", (20, 50)),
                    (">50", (50, None)),
                ]
            },
        },
    }

    # For `PostFilterFilteringBackend` backend
    post_filter_fields = {
        # 'pf_id': '_id',
        # The dictionary key (in this case `title`) is the name of
        # the corresponding GraphQL query argument. The dictionary
        # value could be simple or complex structure (in this case
        # complex). The `field` key points to the `title.raw`, which
        # is the field name in the Elasticsearch document
        # (`PostDocument`). Since `lookups` key is provided, number
        # of lookups is limited to the given set, while term is the
        # default lookup (as specified in `default_lookup`).
        "title": {
            "field": "title.raw",  # Field name in the Elastic doc
            # Available lookups
            "lookups": [
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_TERM,
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_CONTAINS,
                LOOKUP_QUERY_EXCLUDE,
                LOOKUP_QUERY_IN,
            ],
            # Default lookup
            "default_lookup": LOOKUP_FILTER_TERM,
        },
        # The dictionary key (in this case `category`) is the name of
        # the corresponding GraphQL query argument. Since no lookups
        # or default_lookup is provided, defaults are used (all lookups
        # available, term is the default lookup). The dictionary value
        # (in this case `category.raw`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "category": "category.raw",
        # The dictionary key (in this case `tags`) is the name of
        # the corresponding GraphQL query argument. Since no lookups
        # or default_lookup is provided, defaults are used (all lookups
        # available, term is the default lookup). The dictionary value
        # (in this case `tags.raw`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "tags": "tags.raw",
        # The dictionary key (in this case `num_views`) is the name of
        # the corresponding GraphQL query argument. Since no lookups
        # or default_lookup is provided, defaults are used (all lookups
        # available, term is the default lookup). The dictionary value
        # (in this case `num_views`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "num_views": "num_views",
        # The dictionary key (in this case `created_at`) is the name of
        # the corresponding GraphQL query argument. Since no lookups
        # or default_lookup is provided, defaults are used (all lookups
        # available, term is the default lookup). The dictionary value
        # (in this case `created_at`) is the field name in the
        # Elasticsearch document (`PostDocument`).
        "created_at": "created_at",
        "i_do_not_exist": "i_do_not_exist",
    }


class Post(ElasticsearchObjectType):

    class Meta(BasePostMeta):
        pass


class AlternativePost(ElasticsearchObjectType):
    class Meta(BasePostMeta):
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

    class Meta(BasePostMeta):
        pass
