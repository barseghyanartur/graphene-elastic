import graphene

from search_index.documents import Post as PostDocument

from .object_type import Post

__all__ = (
    'SimpleQueryMixin',
    'Query',
    'schema',
)


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


class Query(
    graphene.ObjectType,
    SimpleQueryMixin,
):
    """Query."""


schema = graphene.Schema(query=Query)
