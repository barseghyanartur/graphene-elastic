import graphene
from graphene import Node
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)
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
    'SimpleQueryMixin',
    'FilteredQueryMixin',
    'Query',
    'schema',
)


class Post(ElasticsearchObjectType):

    class Meta(object):
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
            'title': {'boost': 4},
            'content': {'boost': 2},
            'category': None,
        }
        ordering_fields = {
            'id': None,
            'title': 'title.raw',
            'created_at': 'created_at',
            'num_views': 'num_views',
            # 'continent': {
            #     'field': 'continent.name.raw',
            #     'path': 'continent',
            # }
            # 'country': {
            #     'field': 'continent.country.name.raw',
            #     'path': 'continent.country',
            # }
            # 'city': {
            #     'field': 'continent.country.city.name.raw',
            #     'path': 'continent.country.city',
            # }
        }

        ordering_defaults = ('id', 'title',)


class SimpleQueryMixin:
    """Simple query mixin.

    Example usage:

    >>> class Query(
    >>>    SimpleQueryMixin,
    >>>    graphene.ObjectType
    >>> ):
    >>>    pass

    Example query:

        {
          simplePostsList {
            title
            content
            category
            created_at
            comments
          }
        }
    """
    simple_posts_list = graphene.List(Post)

    def resolve_simple_posts_list(self, *args, **kwargs):
        return PostDocument.search().scan()


class FilteredQuerySearchType(graphene.ObjectType):
    """FilteredQueryMixin search helper."""

    title = graphene.String()
    content = graphene.String()


class FilteredQueryMixin:
    """Filtered query mixin.

    Example usage:

    >>> class Query(
    >>>     FilteredQueryMixin,
    >>>     graphene.ObjectType
    >>> ):
    >>>     pass

    Example query:

        {
          filtered_posts_list(page:3, page_size:2) {
            title
            content
            category
            created_at
            comments
          }
        }
    """
    filtered_posts_list = graphene.List(
        Post,
        search=graphene.String(),
        page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=100)
    )

    def resolve_filtered_posts_list(self, *args, **kwargs):
        page = kwargs['page']
        page_size = kwargs['page_size']
        search = kwargs['search'] if 'search' in kwargs else None
        offset_start = (page - 1) * page_size
        offset_end = offset_start + page_size
        return PostDocument.search()[offset_start:offset_end]


class AdvancedQueryMixin:
    """Advanced query mixin.

    Example usage:

    >>> class Query(
    >>>     AdvancedQueryMixin,
    >>>     graphene.ObjectType
    >>> ):
    >>>     pass

    Example query:

        {
          allPostDocuments(page:3, page_size:2) {
            title
            content
            category
            created_at
            tags
          }
        }
    """
    all_post_documents = ElasticsearchConnectionField(Post)


class Query(
    graphene.ObjectType,
    SimpleQueryMixin,
    FilteredQueryMixin,
    AdvancedQueryMixin,
):
    """Query."""


schema = graphene.Schema(query=Query)
