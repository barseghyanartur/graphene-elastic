from collections import OrderedDict
import graphene

from ..constants import (
    DYNAMIC_CLASS_NAME_PREFIX,
    SEPARATOR_LOOKUP_NAME,
    SEPARATOR_LOOKUP_FILTER,
    SEPARATOR_LOOKUP_COMPLEX_VALUE,
    SEPARATOR_LOOKUP_COMPLEX_MULTIPLE_VALUE,
)

__title__ = "graphene_elastic.filter_backends.base"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = ("BaseBackend",)


class BaseBackend(object):

    prefix = None
    has_fields = False

    def __init__(self, connection_field, args=None):
        self.connection_field = connection_field
        self.args = args or {}
        assert self.prefix

    def field_belongs_to(self, field_name):
        raise NotImplementedError

    def add_arg_prefix(self, arg_name):
        return "{}_{}".format(self.prefix, arg_name)

    def get_field_name(self, arg_name):
        if arg_name.startswith(self.prefix):
            return arg_name.lstrip("{}_".format(self.prefix))

    def arg_belongs_to(self, arg_name):
        field_name = self.get_field_name(arg_name)
        if field_name:
            return self.field_belongs_to(field_name)
        return False

    def filter(self, queryset):
        raise NotImplementedError

    # @property
    # def filter_fields(self):
    #     """Filtering filter fields."""
    #     return getattr(
    #         self.connection_field.type._meta.node._meta,
    #         'filter_backend_options',
    #         {}
    #     ).get('filter_fields', {})
    #
    # @property
    # def filter_args_mapping(self):
    #     return {k: k for k, v in self.filter_fields.items()}
    #
    # @property
    # def search_fields(self):
    #     """Search filter fields."""
    #     return getattr(
    #         self.connection_field.type._meta.node._meta,
    #         'filter_backend_options',
    #         {}
    #     ).get('search_fields', {})
    #
    # @property
    # def search_args_mapping(self):
    #     return {k: k for k, v in self.search_fields.items()}
    #
    # @property
    # def ordering_fields(self):
    #     return getattr(
    #         self.connection_field.type._meta.node._meta,
    #         'filter_backend_options',
    #         {}
    #     ).get('ordering_fields', {})
    #
    # @property
    # def ordering_args_mapping(self):
    #     return {k: k for k, v in self.ordering_fields.items()}
    #
    # @property
    # def ordering_defaults(self):
    #     return getattr(
    #         self.connection_field.type._meta.node._meta,
    #         'filter_backend_options',
    #         {}
    #     ).get('ordering_defaults', {})

    @property
    def doc_type(self):
        return self.connection_field.document._doc_type

    @classmethod
    def generic_fields(cls):
        """Generic backend specific filtering fields.

        For instance, for search filter backend it would be
        ``{'search': String()}``.

        :return:
        :rtype dict:
        """
        return {}

    def get_backend_document_fields(self):
        """Get backend document fields.

        :return:
        """
        return OrderedDict()

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
        raise NotImplementedError

    def get_backend_default_fields_params(self):
        """Backend default filter params.

        :rtype: dict
        :return:
        """
        return {}

    def get_backend_fields(self, items, is_filterable_func, get_type_func):
        """Construct backend fields.

        :param items:
        :param is_filterable_func:
        :param get_type_func:
        :return:
        """
        params = self.get_backend_default_fields_params()
        for _k, _v in items:
            if is_filterable_func(_k):
                # Getting other backend specific fields (schema dependant)
                if self.field_belongs_to(_k):
                    params.update(
                        {_k: self.get_field_type(_k, _v, get_type_func(_v))}
                    )

        return {
            self.prefix: graphene.Argument(
                type(
                    "{}{}{}BackendFilter".format(
                        DYNAMIC_CLASS_NAME_PREFIX,
                        self.prefix.title(),
                        self.connection_field.type.__name__
                    ),
                    (graphene.InputObjectType,),
                    params,
                )
            )
        }

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
