import graphene
from graphene_elastic import ElasticsearchConnectionField

from .object_type import Post, AlternativePost, PostSuggest

__all__ = (
    'ConnectionQueryMixin',
    'Query',
    'schema',
)


class ConnectionQueryMixin:
    """Advanced query mixin.

    Example usage:

    >>> class Query(
    >>>     ConnectionQueryMixin,
    >>>     graphene.ObjectType
    >>> ):
    >>>     pass

    Example query:

        {
          allPostDocuments(first:12, after:"YXJyYXljb25uZWN0aW9uOjEx") {
            pageInfo {
              startCursor
              endCursor
              hasNextPage
              hasPreviousPage
            }
            edges {
              cursor
              node {
                category
                title
                content
                numViews
              }
            }
          }
        }
    """
    all_post_documents = ElasticsearchConnectionField(Post)
    all_post_suggestions = ElasticsearchConnectionField(PostSuggest)
    alternative_post_documents = ElasticsearchConnectionField(AlternativePost)


class Query(
    graphene.ObjectType,
    ConnectionQueryMixin,
):
    """Query."""


schema = graphene.Schema(query=Query)
