"""
Some overrides of the original ``graphql_relay.connection.connection``
module. For sanity and ease of updates/sync with modifications from upstream,
this module isn't formatted in accordance with the rest of the package.
Pull requests code-style changes wouldn't be accepted.
"""
import re
from collections import (
    # Iterable,
    OrderedDict,
)
# from functools import partial

# from graphql_relay import connection_from_list

from graphene.types import (
    # Boolean,
    Enum,
    # Int,
    Interface,
    List,
    NonNull,
    Scalar,
    String,
    Union,
)
from graphene.types.field import Field
from graphene.types.objecttype import ObjectType, ObjectTypeOptions
# from graphene.utils.thenables import maybe_thenable
# from graphene.relay.node import is_node

from graphene.relay import PageInfo


__title__ = 'graphene_elastic.relay.connection'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'Connection',
    'ConnectionOptions',
)


# class PageInfo(ObjectType):
#     class Meta:
#         description = (
#             "The Relay compliant `PageInfo` type, containing data necessary to"
#             " paginate this connection."
#         )
#
#     has_next_page = Boolean(
#         required=True,
#         name="hasNextPage",
#         description="When paginating forwards, are there more items?",
#     )
#
#     has_previous_page = Boolean(
#         required=True,
#         name="hasPreviousPage",
#         description="When paginating backwards, are there more items?",
#     )
#
#     start_cursor = String(
#         name="startCursor",
#         description="When paginating backwards, the cursor to continue.",
#     )
#
#     end_cursor = String(
#         name="endCursor",
#         description="When paginating forwards, the cursor to continue.",
#     )


class Facets(ObjectType):
    class Meta:
        description = (
            "The Relay compliant `Facets` type, containing facets data."
        )


class ConnectionOptions(ObjectTypeOptions):
    node = None


class Connection(ObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, node=None, name=None, **options):
        _meta = ConnectionOptions(cls)
        assert node, "You have to provide a node in {}.Meta".format(cls.__name__)
        assert isinstance(node, NonNull) or issubclass(
            node, (Scalar, Enum, ObjectType, Interface, Union, NonNull)
        ), ('Received incompatible node "{}" for Connection {}.').format(
            node, cls.__name__
        )

        base_name = re.sub("Connection$", "", name or cls.__name__) or node._meta.name
        if not name:
            name = "{}Connection".format(base_name)

        edge_class = getattr(cls, "Edge", None)
        _node = node

        class EdgeBase(object):
            node = Field(_node, description="The item at the end of the edge")
            cursor = String(required=True, description="A cursor for use in pagination")

        class EdgeMeta:
            description = "A Relay edge containing a `{}` and its cursor.".format(
                base_name
            )

        edge_name = "{}Edge".format(base_name)
        if edge_class:
            edge_bases = (edge_class, EdgeBase, ObjectType)
        else:
            edge_bases = (EdgeBase, ObjectType)

        edge = type(edge_name, edge_bases, {"Meta": EdgeMeta})
        cls.Edge = edge

        from graphene_elastic.types.json_string import JSONString

        options["name"] = name
        _meta.node = node
        _meta.fields = OrderedDict(
            [
                (
                    "page_info",
                    Field(
                        PageInfo,
                        name="pageInfo",
                        required=True,
                        description="Pagination data for this connection.",
                    ),
                ),
                (
                    "edges",
                    Field(
                        NonNull(List(edge)),
                        description="Contains the nodes in this connection.",
                    ),
                ),
                # TODO: Construct this dynamically from the filter backends.
                (
                    "facets",
                    Field(
                        JSONString,
                        name="facets",
                        required=False,
                        description="Pagination data for this connection.",
                    ),
                ),
            ]
        )
        # for backend_cls in backends:
        #     if backend_cls.has_connection_fields:
        #         backend = backend_cls()
        #         connection_fields_type = backend.get_backend_connection_fields_type()
        #         if connection_fields_type:
        #             try:
        #                 _meta.fields.update(connection_fields_type)
        #             except:
        #                 pass
        return super(Connection, cls).__init_subclass_with_meta__(
            _meta=_meta, **options
        )


# class IterableConnectionField(Field):
#     def __init__(self, type, *args, **kwargs):
#         kwargs.setdefault("before", String())
#         kwargs.setdefault("after", String())
#         kwargs.setdefault("first", Int())
#         kwargs.setdefault("last", Int())
#         super(IterableConnectionField, self).__init__(type, *args, **kwargs)
#
#     @property
#     def type(self):
#         type = super(IterableConnectionField, self).type
#         connection_type = type
#         if isinstance(type, NonNull):
#             connection_type = type.of_type
#
#         if is_node(connection_type):
#             raise Exception(
#                 "ConnectionFields now need a explicit ConnectionType for Nodes.\n"
#                 "Read more: https://github.com/graphql-python/graphene/blob/v2.0.0/UPGRADE-v2.0.md#node-connections"
#             )
#
#         assert issubclass(connection_type, Connection), (
#             '{} type have to be a subclass of Connection. Received "{}".'
#         ).format(self.__class__.__name__, connection_type)
#         return type
#
#     @classmethod
#     def resolve_connection(cls, connection_type, args, resolved):
#         if isinstance(resolved, connection_type):
#             return resolved
#
#         assert isinstance(resolved, Iterable), (
#             "Resolved value from the connection field have to be iterable or instance of {}. "
#             'Received "{}"'
#         ).format(connection_type, resolved)
#         connection = connection_from_list(
#             resolved,
#             args,
#             connection_type=connection_type,
#             edge_type=connection_type.Edge,
#             pageinfo_type=PageInfo,
#         )
#         connection.iterable = resolved
#         return connection
#
#     @classmethod
#     def connection_resolver(cls, resolver, connection_type, root, info, **args):
#         resolved = resolver(root, info, **args)
#
#         if isinstance(connection_type, NonNull):
#             connection_type = connection_type.of_type
#
#         on_resolve = partial(cls.resolve_connection, connection_type, args)
#         return maybe_thenable(resolved, on_resolve)
#
#     def get_resolver(self, parent_resolver):
#         resolver = super(IterableConnectionField, self).get_resolver(parent_resolver)
#         return partial(self.connection_resolver, resolver, self.type)
#
#
# ConnectionField = IterableConnectionField
