"""Compound search backend."""
import copy
import graphene

from .base import BaseSearchFilterBackend
from ...constants import (
    DYNAMIC_CLASS_NAME_PREFIX,
    ALL,
    VALUE,
    BOOST,
)
from ...helpers import to_pascal_case
from .query_backends import (
    MatchQueryBackend,
    # NestedQueryBackend,
)

__title__ = 'graphene_elastic.filter_backends.search.compound'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'CompoundSearchFilterBackend',
)


class CompoundSearchFilterBackend(BaseSearchFilterBackend):
    """Compound search backend."""

    prefix = 'search'
    has_query_fields = True
    query_backends = [
        MatchQueryBackend,
        # NestedQueryBackend,
    ]

    @property
    def search_fields(self):
        """Search filter fields."""
        search_fields = getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('search_fields', {})
        return copy.deepcopy(search_fields)

    @property
    def search_args_mapping(self):
        return {field: field for field, value in self.search_fields.items()}

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        return field_name in self.search_fields

    def get_backend_default_query_fields_params(self):
        """Get backend default filter params.

        :rtype: dict
        :return:
        """
        return {ALL: graphene.String()}

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
        params = {
            VALUE: base_field_type,  # Value to search on. Required.
            BOOST: graphene.Int(),  # Boost the given field with. Optional.
        }
        return graphene.Argument(
            type(
                "{}{}{}{}".format(
                    DYNAMIC_CLASS_NAME_PREFIX,
                    to_pascal_case(self.prefix),
                    self.connection_field.type.__name__,
                    to_pascal_case(field_name)
                ),
                (graphene.InputObjectType,),
                params,
            )
        )
