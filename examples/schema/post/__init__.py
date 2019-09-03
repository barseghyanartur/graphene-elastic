import graphene

from .connection import (
    ConnectionQueryMixin,
    Query as ConnectionQuery,
    schema as connection_schema,
)
from .filtered_list import (
    FilteredQueryMixin,
    Query as FilteredQuery,
    schema as filtered_schema,
)
from .object_type import Post
from .simple_list import (
    SimpleQueryMixin,
    Query as SimpleQuery,
    schema as simple_schema,
)

__all__ = (
    'Query',
    'schema',
)


class Query(
    graphene.ObjectType,
    SimpleQueryMixin,
    FilteredQueryMixin,
    ConnectionQueryMixin,
):
    """Query."""


schema = graphene.Schema(query=Query)
