import graphene
from graphene_elastic import ElasticsearchConnectionField

from .object_type import Post, AlternativePost, PostForUser

__all__ = (
    'ConnectionQueryMixin',
    'Query',
    'schema',
)


def get_queryset_for_user(document, info, **args):
    """Get queryset for user. Works with Django only. Use this as an example.

    In order to have this working, log into django admin (localhost:8000/admin)
    and make a query to the `post_documents_for_user` endpoint.

        query PostsQuery {
          postDocumentsForUser {
            edges {
              node {
                id
                title
                userId
              }
            }
          }
        }

    As a result you will only get documents for the user with id equal to the
    id of the logged in user.
    """
    try:
        user_id = info.context.user.id
    except AttributeError:
        user_id = -1  # There's no user with id equal to -1
    return document.search().filter('term', user_id=user_id)


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
    # Standard example
    all_post_documents = ElasticsearchConnectionField(Post)
    # Example requiring authentication (works with Django only)
    post_documents_for_user = ElasticsearchConnectionField(
        PostForUser,
        get_queryset=get_queryset_for_user
    )
    # Alternative Post behaviour
    alternative_post_documents = ElasticsearchConnectionField(AlternativePost)


class Query(
    graphene.ObjectType,
    ConnectionQueryMixin,
):
    """Query."""


schema = graphene.Schema(query=Query)
