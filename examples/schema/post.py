from enum import Enum
import graphene
from graphene import Node
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)
from graphene_elastic.types.json_string import JSONString
from graphene_elastic.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
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
    # title = JSONString(name='title')

    class Meta(object):
        document = PostDocument
        interfaces = (Node,)
        filter_backends = [
            FilteringFilterBackend,
            SearchFilterBackend,
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
          simple_posts_list {
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


class NoValue(Enum):

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


@graphene.Enum.from_enum
class Direction(NoValue):
    ASC = 'asc'
    DESC = 'desc'


from graphene_elastic.filter_backends.queries import *  # NOQA


# class Complex(graphene.InputObjectType):
#
#     term = Term()
#     terms = Terms()
#     range = Range()
#     exists = Exists()
#     prefix = Prefix()
#     starts_with = StartsWith()
#     wildcard = Wildcard()
#     geo_distance = GeoDistance()
#     geo_polygon = GeoPolygon()
#     geo_bounding_box = GeoBoundingBox()
#     contains = Contains()
#     # In = In()  # NOQA
#     gt = Gt()
#     gte = Gte()
#     lt = Lt()
#     lte = Lte()
#     endswith = EndsWith()
#     is_null = IsNull()
#     exclude = Exclude()

#
# complex_params = {
#     'term': Term(),
#     'terms': Terms(),
#     'range': Range(),
#     'exists': Exists(),
#     'prefix': Prefix(),
#     'starts_with': StartsWith(),
#     'wildcard': Wildcard(),
#     'geo_distance': GeoDistance(),
#     'geo_polygon': GeoPolygon(),
#     'geo_bounding_box': GeoBoundingBox(),
#     'contains': Contains(),
#     'in': In(),
#     'gt': Gt(),
#     'gte': Gte(),
#     'lt': Lt(),
#     'lte': Lte(),
#     'ends_with': EndsWith(),
#     'is_null': IsNull(),
#     'exclude': Exclude(),
# }
#
# Complex = type(
#     'Complex',
#     (graphene.InputObjectType,),
#     complex_params
# )


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
          advanced_posts_list(page:3, page_size:2) {
            title
            content
            category
            created_at
            comments
          }
        }
    """
    # advanced_posts_list = ElasticsearchFilterConnectionField(Post)
    all_post_documents = ElasticsearchConnectionField(
        Post,
        # default_field=graphene.String(),
        # query=graphene.String(),
        # complex=graphene.Argument(Complex),
        # search=graphene.String()
    )


class Query(
    graphene.ObjectType,
    SimpleQueryMixin,
    FilteredQueryMixin,
    AdvancedQueryMixin,
):
    """Query."""


schema = graphene.Schema(
    query=Query,
    # types=[Post]
)
