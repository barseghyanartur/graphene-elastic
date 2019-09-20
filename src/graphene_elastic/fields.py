from __future__ import absolute_import

# from decimal import Decimal

from collections import Iterable, OrderedDict
from functools import partial, reduce

import graphene
# from graphene import NonNull
# from graphql_relay import connection_from_list
import elasticsearch_dsl
from promise import Promise
from graphene.relay import ConnectionField, PageInfo
from graphene.types.argument import to_arguments
from graphene.types.dynamic import Dynamic
from graphene.types.structures import Structure

from .advanced_types import (
    FileFieldType,
    PointFieldType,
    MultiPolygonFieldType,
)
from .arrayconnection import connection_from_list_slice
from .converter import (
    convert_elasticsearch_field,
    ElasticsearchConversionError,
)
from .filter_backends import (
    SearchFilterBackend,
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
)
from .logging import logger
from .registry import get_global_registry
from .settings import graphene_settings
from .types import ElasticsearchObjectType
from .utils import get_node_from_global_id  # get_model_reference_fields

__title__ = "graphene_elastic.fields"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = ("ElasticsearchConnectionField",)


# def json_default(obj):
#     if isinstance(obj, Decimal):
#         return str(obj)  # String version
#     return obj


class ElasticsearchConnectionField(ConnectionField):
    def __init__(self, type, *args, **kwargs):
        self.on = kwargs.pop("on", False)  # From graphene-django
        self.max_limit = kwargs.pop(
            "max_limit", graphene_settings.RELAY_CONNECTION_MAX_LIMIT
        )  # From graphene-django
        self.enforce_first_or_last = kwargs.pop(
            "enforce_first_or_last",
            graphene_settings.RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST,
        )  # From graphene-django
        get_queryset = kwargs.pop("get_queryset", None)
        if get_queryset:
            assert callable(
                get_queryset
            ), "Attribute `get_queryset` on {} must be callable.".format(self)
        self._get_queryset = get_queryset

        super(ElasticsearchConnectionField, self).__init__(
            type, *args, **kwargs
        )

    @property
    def type(self):
        # from .types import ElasticsearchObjectType
        _type = super(ConnectionField, self).type
        assert issubclass(
            _type, ElasticsearchObjectType
        ), "ElasticsearchConnectionField only accepts " \
           "ElasticsearchObjectType types"
        assert (
            _type._meta.connection
        ), "The type {} doesn't have a connection".format(_type.__name__)
        return _type._meta.connection

    # @property
    # def connection_type(self):  # From graphene-django
    #     type = self.type
    #     if isinstance(type, NonNull):
    #         return type.of_type
    #     return type

    @property
    def node_type(self):
        return self.type._meta.node

    @property
    def document(self):
        return self.node_type._meta.document

    @property
    def doc_type(self):
        return self.document._doc_type

    # def get_manager(self):  # From graphene-django
    #     if self.on:
    #         return getattr(self.document, self.on)
    #     else:
    #         return self.document.search()

    @property
    def registry(self):
        return getattr(self.node_type._meta, "registry", get_global_registry())

    @property
    def args(self):
        return to_arguments(
            self._base_args or OrderedDict(),
            dict(self.field_args, **self.reference_args),
        )

    # @property
    # def filter_fields(self):
    #     return getattr(self.node_type._meta, "filter_fields", {})
    #
    # @property
    # def filter_args_mapping(self):
    #     # TODO: Move this to backend
    #     return {k: k for k, v in self.filter_fields.items()}
    #
    # @property
    # def search_fields(self):
    #     return getattr(self.node_type._meta, "search_fields", {})
    #
    # @property
    # def search_args_mapping(self):
    #     # TODO: Move this to backend
    #     return {k: k for k, v in self.search_fields.items()}
    #
    # @property
    # def ordering_fields(self):
    #     return getattr(self.node_type._meta, "ordering_fields", {})
    #
    # @property
    # def ordering_args_mapping(self):
    #     # TODO: Move this to backend
    #     return {k: k for k, v in self.ordering_fields.items()}
    #
    # @property
    # def ordering_defaults(self):
    #     return getattr(self.node_type._meta, "ordering_defaults", [])

    @property
    def default_filter_backends(self):
        return [
            SearchFilterBackend,
            FilteringFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]

    @property
    def filter_backends(self):
        return getattr(
            self.node_type._meta,
            "filter_backends",
            self.default_filter_backends,
        )

    @args.setter
    def args(self, args):
        self._base_args = args

    def _field_args(self, items):
        def is_filterable(k):
            """
            Args:
                k (str): field name.
            Returns:
                bool
            """
            if k not in self.doc_type.mapping.properties.properties._d_:
                return False
            try:
                converted = convert_elasticsearch_field(
                    self.doc_type.mapping.properties.properties._d_.get(k),
                    self.registry,
                )
            except ElasticsearchConversionError:
                return False
            if isinstance(converted, (ConnectionField, Dynamic)):
                return False
            if callable(getattr(converted, "type", None)) and isinstance(
                converted.type(),
                (
                    FileFieldType,
                    PointFieldType,
                    MultiPolygonFieldType,
                    graphene.Union,
                ),
            ):
                return False
            return True

        def get_type(v):
            if isinstance(v.type, Structure):
                return v.type.of_type()
            return v.type()

        # Filter fields are here: self.node_type._meta.filter_fields
        # Search fields are here: self.node_type._meta.search_fields

        params = {}

        for backend_cls in self.filter_backends:
            backend = backend_cls(self)
            if backend.has_fields:
                params.update(
                    backend.get_backend_fields(
                        items=items,
                        is_filterable_func=is_filterable,
                        get_type_func=get_type,
                    )
                )

        return params

    @property
    def field_args(self):
        return self._field_args(self.fields.items())

    @property
    def reference_args(self):
        def get_reference_field(r, kv):
            field = kv[1]
            # TODO: Find out whether this is applicable to Elasticsearch
            if callable(getattr(field, "get_type", None)):
                _type = field.get_type()
                if _type:
                    node = _type._type._meta
                    if "id" in node.fields and not issubclass(
                        node.document, (elasticsearch_dsl.InnerDoc,)
                    ):
                        r.update({kv[0]: node.fields["id"]._type.of_type()})
            return r

        return reduce(get_reference_field, self.fields.items(), {})

    @property
    def fields(self):
        # We might need self._type._doc_type.mapping.properties.properties._d_
        return self._type._meta.fields

    def get_queryset(self, document, info, **args):
        if args:
            # reference_fields = get_model_reference_fields(self.model)
            reference_fields = {}
            hydrated_references = {}
            for arg_name, arg in args.copy().items():
                if arg_name in reference_fields:
                    reference_obj = get_node_from_global_id(
                        reference_fields[arg_name], info, args.pop(arg_name)
                    )
                    hydrated_references[arg_name] = reference_obj
            args.update(hydrated_references)

        if self._get_queryset:
            queryset_or_filters = self._get_queryset(document, info, **args)
            if isinstance(queryset_or_filters, elasticsearch_dsl.Search):
                return queryset_or_filters
            else:
                args.update(queryset_or_filters)
        qs = document.search()

        for backend_cls in self.filter_backends:
            backend = backend_cls(self, args=dict(args))
            qs = backend.filter(qs)

        try:
            logger.debug(qs.to_dict())
        except Exception as err:
            logger.debug(err)
        return qs

    def default_resolver(self, _root, info, **args):
        args = args or {}
        connection_args = {
            "first": args.pop("first", None),
            "last": args.pop("last", None),
            "before": args.pop("before", None),
            "after": args.pop("after", None),
            "max_limit": args.pop(
                "max_limit",
                graphene_settings.RELAY_CONNECTION_MAX_LIMIT
            ),
            "enforce_first_or_last": args.pop(
                "enforce_first_or_last",
                graphene_settings.RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST
            ),
        }

        _id = args.pop("id", None)

        if _id is not None:
            iterables = [get_node_from_global_id(self.node_type, info, _id)]
            list_length = 1
        # TODO: The next line never happens. We might want to make sure
        # functionality that must be there is present
        elif callable(getattr(self.document, "search", None)):
            iterables = self.get_queryset(self.document, info, **args)
            list_length = iterables.count()
        else:
            iterables = []
            list_length = 0
        connection = connection_from_list_slice(
            list_slice=iterables,
            args=connection_args,
            list_length=list_length,
            list_slice_length=list_length,
            connection_type=self.type,
            edge_type=self.type.Edge,
            pageinfo_type=graphene.PageInfo,
        )
        connection.iterable = iterables
        connection.list_length = list_length
        return connection

    def chained_resolver(self, resolver, is_partial, root, info, **args):
        if not bool(args) or not is_partial:
            resolved = resolver(root, info, **args)
            if resolved is not None:
                return resolved
        return self.default_resolver(root, info, **args)

    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        if isinstance(resolved, connection_type):
            return resolved

        assert isinstance(resolved, Iterable), (
            "Resolved value from the connection field have to be iterable or "
            "instance of {}. "
            'Received "{}"'
        ).format(connection_type, resolved)

        _len = resolved.hits.total["value"]

        connection = connection_from_list_slice(
            resolved.hits,
            args,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=connection_type,
            edge_type=connection_type.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = resolved
        connection.length = _len
        return connection

    @classmethod
    def connection_resolver(cls,
                            resolver,
                            connection_type,
                            root,
                            info,
                            **args):
        first = args.get("first")
        last = args.get("last")
        enforce_first_or_last = args.get("enforce_first_or_last")
        max_limit = args.get("max_limit")

        if enforce_first_or_last:
            assert first or last, (
                "You must provide a `first` or `last` value to properly "
                "paginate the `{}` connection."
            ).format(info.field_name)

        if max_limit:
            if first:
                assert first <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds "
                    "the `first` limit of {} records."
                ).format(first, info.field_name, max_limit)
                args["first"] = min(first, max_limit)

            if last:
                assert last <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds "
                    "the `last` limit of {} records."
                ).format(last, info.field_name, max_limit)
                args["last"] = min(last, max_limit)

        iterable = resolver(root, info, **args)
        if isinstance(connection_type, graphene.NonNull):
            connection_type = connection_type.of_type

        on_resolve = partial(cls.resolve_connection, connection_type, args)

        if Promise.is_thenable(iterable):
            return Promise.resolve(iterable).then(on_resolve)

        return on_resolve(iterable)

    def get_resolver(self, parent_resolver):
        super_resolver = self.resolver or parent_resolver
        resolver = partial(
            self.chained_resolver,
            super_resolver,
            isinstance(super_resolver, partial),
        )
        return partial(
            self.connection_resolver,
            resolver,
            self.type,
            max_limit=self.max_limit,
            enforce_first_or_last=self.enforce_first_or_last
        )
