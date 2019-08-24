import graphene

from graphene_elastic import ElasticsearchObjectType

from search_index.documents import User as UserDocument


__all__ = (
    'User',
    'Query',
    'schema',
)


class User(ElasticsearchObjectType):
    class Meta:
        document = UserDocument


class Query(graphene.ObjectType):
    users = graphene.List(User)

    def resolve_users(self, info):
        return UserDocument.search().scan()


schema = graphene.Schema(
    query=Query,
    auto_camelcase=False
)
