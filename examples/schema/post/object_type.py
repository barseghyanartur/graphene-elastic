from graphene import Node
from graphene_elastic import ElasticsearchObjectType
from graphene_elastic.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
)
from graphene_elastic.constants import (
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_IN,
)

from search_index.documents import Post as PostDocument

__all__ = (
    'Post',
)


class Post(ElasticsearchObjectType):

    class Meta:

        document = PostDocument
        interfaces = (Node,)
        filter_backends = [
            FilteringFilterBackend,
            SearchFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]
        filter_fields = {
            'id': '_id',
            'title': {
                'field': 'title.raw',
                'lookups': [
                    LOOKUP_FILTER_TERM,
                    LOOKUP_FILTER_TERMS,
                    LOOKUP_FILTER_PREFIX,
                    LOOKUP_FILTER_WILDCARD,
                    LOOKUP_QUERY_IN,
                    LOOKUP_QUERY_EXCLUDE,
                ],
                'default_lookup': LOOKUP_FILTER_TERM,
            },
            'category': 'category.raw',
            'tags': 'tags.raw',
            'num_views': 'num_views',
            'i_do_not_exist': 'i_do_not_exist',
        }
        search_fields = {
            'title': {'field': 'title', 'boost': 4},
            'content': {'boost': 2},
            'category': None,
        }
        ordering_fields = {
            'title': 'title.raw',
            'created_at': 'created_at',
            'num_views': 'num_views',
        }

        ordering_defaults = (
            '-num_views',
            'title.raw',
        )
