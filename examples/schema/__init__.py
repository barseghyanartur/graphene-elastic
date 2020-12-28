import graphene
from .animal import Query as AnimalQuery
from .post import Query as PostQuery
from .read_only_animal import Query as ReadOnlyAnimalQuery
from .user import Query as UserQuery

__all__ = (
    'Query',
    'schema',
)


class Query(
    AnimalQuery,
    ReadOnlyAnimalQuery,
    PostQuery,
    UserQuery,
    graphene.ObjectType,
):
    """GraphQL query"""


schema = graphene.Schema(
    query=Query,
    # auto_camelcase=False,
    # types=[Post, User],
)
