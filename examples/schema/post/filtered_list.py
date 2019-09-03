import graphene

from search_index.documents import Post as PostDocument

from .object_type import Post

__all__ = (
    'FilteredQueryMixin',
    'Query',
    'schema',
)


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


class Query(
    graphene.ObjectType,
    FilteredQueryMixin,
):
    """Query."""


schema = graphene.Schema(query=Query)
