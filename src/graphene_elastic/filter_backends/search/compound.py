"""Compound search backend."""

from .base import BaseSearchFilterBackend
from .query_backends import (
    MatchQueryBackend,
    NestedQueryBackend,
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

    query_backends = [
        MatchQueryBackend,
        # NestedQueryBackend,
    ]
