import enum
import graphene

from ..base import BaseBackend
from ...constants import DYNAMIC_CLASS_NAME_PREFIX

__title__ = 'graphene_elastic.filter_backends.ordering.common'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'SourceFilterBackend',
)


class SourceFilterBackend(BaseBackend):
    """Source filter backend."""

    prefix = 'source'
    has_fields = True

    def field_belongs_to(self, field_name):
        return field_name in self.source_fields

    def get_backend_default_fields_params(self):
        """Get backend default filter params.

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
        _keys = list(
            self.connection_field.type._meta.node._meta.fields.keys()
        )
        _keys.remove('_id')
        params = zip(_keys, _keys)
        return {
            self.prefix: graphene.Argument(
                graphene.List(
                    graphene.Enum.from_enum(
                        enum.Enum(
                            "{}{}{}BackendEnum".format(
                                DYNAMIC_CLASS_NAME_PREFIX,
                                self.prefix.title(),
                                self.connection_field.type.__name__
                            ),
                            params
                        )
                    )
                )
            )
        }

    @property
    def source_fields(self):
        """Source filter fields."""
        return getattr(
            self.connection_field.type._meta.node._meta,
            'source_fields',
            {}
        )

    @property
    def source_args_mapping(self):
        return {k: k for k, v in self.source_fields.items()}

    def prepare_source_fields(self):
        """Prepare source fields.

        Possible structures:

            source_fields = ["title"]

        Or:

            search_fields = ["title", "author.*"]

        Or:

            source = {
                "includes": ["title", "author.*"],
                "excludes": [ "*.description" ]
            }

        :return: Filtering options.
        :rtype: dict
        """
        source_args = dict(self.args).get(self.prefix, [])

        source_fields = dict(self.source_fields)

        if source_args:
            return source_args
        return source_fields

    def get_source_query_params(self):
        """Get highlight query params.

        :return: List of search query params.
        :rtype: list
        """
        source_args = dict(self.args).get(self.prefix, {})
        return source_args

    def filter(self, queryset):
        """Filter.

        :param queryset:
        :return:
        """
        source_fields = self.prepare_source_fields()

        if source_fields:
            queryset = queryset.source(source_fields)

        return queryset
