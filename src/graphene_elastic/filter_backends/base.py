from collections import OrderedDict
import graphene

from ..constants import (
    DYNAMIC_CLASS_NAME_PREFIX,
    SEPARATOR_LOOKUP_NAME,
    SEPARATOR_LOOKUP_FILTER,
    SEPARATOR_LOOKUP_COMPLEX_VALUE,
    SEPARATOR_LOOKUP_COMPLEX_MULTIPLE_VALUE,
)
from ..helpers import to_pascal_case

__title__ = "graphene_elastic.filter_backends.base"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = ("BaseBackend",)


class BaseBackend(object):
    """Base backend."""

    # Prefix for the backend. This is used to isolate the backend variables
    # but also is used in dynamically constructing the class names of
    # `graphene` types.
    prefix = None

    # If set to True, an attempt will be made to construct the GraphQL query
    # fields for backend.
    has_query_fields = False

    # If set to True, an attempt will be made to construct the connection
    # fields for backend.
    has_connection_fields = False

    def __init__(self, connection_field, args=None):
        self.connection_field = connection_field
        self.args = args or {}
        assert self.prefix

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        raise NotImplementedError

    # def add_arg_prefix(self, arg_name):
    #     return "{}_{}".format(self.prefix, arg_name)
    #
    # def get_field_name(self, arg_name):
    #     """Get field name.
    #
    #     :param arg_name:
    #     :return:
    #     """
    #     if arg_name.startswith(self.prefix):
    #         return arg_name.lstrip("{}_".format(self.prefix))
    #
    # def arg_belongs_to(self, arg_name):
    #     field_name = self.get_field_name(arg_name)
    #     if field_name:
    #         return self.field_belongs_to(field_name)
    #     return False

    def filter(self, queryset):
        """Filter. This method alters current queryset.

        :param queryset:
        :return:
        """
        raise NotImplementedError

    @property
    def doc_type(self):
        """Shortcut to the Elasticsearch document type.

        :return:
        """
        return self.connection_field.document._doc_type

    @classmethod
    def generic_query_fields(cls):
        """Generic backend specific query fields.

        For instance, for search filter backend it would be
        ``{'search': String()}``.

        :return:
        :rtype dict:
        """
        return {}

    def get_backend_document_fields(self):
        """Get additional document fields for the backend.

        For instance, the ``Highlight`` backend add additional field named
        ``highlight`` to the list of fields.

        Sample query:

            query {
              allPostDocuments(search:{title:{value:"alice"}}) {
                edges {
                  node {
                    id
                    title
                    highlight
                  }
                }
              }
            }

        Sample response:

            {
              "data": {
                "allPostDocuments": {
                  "edges": [
                    {
                      "node": {
                        "id": "UG9zdDp5a1ppVlcwQklwZ2dXbVlJQV91Rw==",
                        "title": "thus Alice style",
                        "highlight": {
                          "title": [
                            "thus <b>Alice</b> style"
                          ]
                        }
                      }
                    },
                    ...
                  ]
                }
              }
            }

        That ``highlight`` part on both sample query and sample response
        isn't initially available on the connection level, but added with
        help of the filter backend.
        :return:
        """
        return OrderedDict()

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
        raise NotImplementedError

    def get_backend_default_query_fields_params(self):
        """Get default query fields params for the backend.

        :rtype: dict
        :return:
        """
        return {}

    def get_backend_query_fields(self,
                                 items,
                                 is_filterable_func,
                                 get_type_func):
        """Construct backend query fields.

        :param items:
        :param is_filterable_func:
        :param get_type_func:
        :return:
        """
        params = self.get_backend_default_query_fields_params()
        for field, value in items:
            if is_filterable_func(field):
                # Getting other backend specific fields (schema dependant)
                if self.field_belongs_to(field):
                    params.update({
                        field: self.get_field_type(
                            field,
                            value,
                            get_type_func(value)
                        )
                    })

        return {
            self.prefix: graphene.Argument(
                type(
                    "{}{}{}BackendFilter".format(
                        DYNAMIC_CLASS_NAME_PREFIX,
                        to_pascal_case(self.prefix),
                        self.connection_field.type.__name__
                    ),
                    (graphene.InputObjectType,),
                    params,
                )
            )
        }

    def get_backend_connection_fields_type(self):
        """Get backend connection fields type.

        Typical use-case - a backend that alters the Connection object
        and adds additional fields next to `edges` and `pageInfo` (see
        the `graphene_elastic.relay.connection.Connection` for more
        information).

        :return:
        """
        return {}

    def get_backend_connection_fields(self):
        """Get backend connection fields.

        Typical use-case - a backend that alters the Connection object
        and adds additional fields next to `edges` and `pageInfo` (see
        the `graphene_elastic.relay.connection.Connection` for more
        information).

        :rtype dict:
        :return:
        """
        return {}

    def alter_connection(self, connection, slice):
        """Alter connection object.

        You can add various properties here, returning the altered object.
        Typical use-case would be adding facets to the connection.

        :param connection:
        :param slice:
        :return:
        """
        return connection

    @classmethod
    def split_lookup_name(cls, value, maxsplit=-1):
        """Split lookup value.

        :param value: Value to split.
        :param maxsplit: The `maxsplit` option of `string.split`.
        :type value: str
        :type maxsplit: int
        :return: Lookup value split into a list.
        :rtype: list
        """
        return value.split(SEPARATOR_LOOKUP_NAME, maxsplit)

    @classmethod
    def split_lookup_filter(cls, value, maxsplit=-1):
        """Split lookup filter.

        :param value: Value to split.
        :param maxsplit: The `maxsplit` option of `string.split`.
        :type value: str
        :type maxsplit: int
        :return: Lookup filter split into a list.
        :rtype: list
        """
        return value.split(SEPARATOR_LOOKUP_FILTER, maxsplit)

    @classmethod
    def split_lookup_complex_value(cls, value, maxsplit=-1):
        """Split lookup complex value.

        :param value: Value to split.
        :param maxsplit: The `maxsplit` option of `string.split`.
        :type value: str
        :type maxsplit: int
        :return: Lookup filter split into a list.
        :rtype: list
        """
        return value.split(SEPARATOR_LOOKUP_COMPLEX_VALUE, maxsplit)

    @classmethod
    def split_lookup_complex_multiple_value(cls, value, maxsplit=-1):
        """Split lookup complex multiple value.

        :param value: Value to split.
        :param maxsplit: The `maxsplit` option of `string.split`.
        :type value: str
        :type maxsplit: int
        :return: Lookup filter split into a list.
        :rtype: list
        """
        return value.split(SEPARATOR_LOOKUP_COMPLEX_MULTIPLE_VALUE, maxsplit)

    @classmethod
    def apply_filter(cls, queryset, options=None, args=None, kwargs=None):
        """Apply filter.

        :param queryset:
        :param options:
        :param args:
        :param kwargs:
        :return:
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        return queryset.filter(*args, **kwargs)

    @classmethod
    def apply_query(cls, queryset, options=None, args=None, kwargs=None):
        """Apply query.

        :param queryset:
        :param options:
        :param args:
        :param kwargs:
        :return:
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        return queryset.query(*args, **kwargs)
