from .post import Query as PostQuery
from .user import Query as UserQuery
import graphene

__all__ = (
    'Query',
    'schema',
)


class Query(
    PostQuery,
    UserQuery,
    graphene.ObjectType,
):
    """GraphQL query"""


schema = graphene.Schema(
    query=Query,
    # auto_camelcase=False,
    # types=[Post, User]
)
