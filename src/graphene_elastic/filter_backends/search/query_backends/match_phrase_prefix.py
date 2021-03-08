import copy

from elasticsearch_dsl.query import Q

from ....constants import (
    ALL,
    VALUE,
)

from .base import BaseSearchQueryBackend

__title__ = 'graphene_elastic.filter_backends.search.query_backends.' \
            'match_phrase_prefix'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('MatchPhrasePrefixQueryBackend',)


class MatchPhrasePrefixQueryBackend(BaseSearchQueryBackend):
    """Match phrase query backend."""

    query_type = 'match_phrase_prefix'

    def construct_search(self):
        """Construct search.

        :return:
        """
        query_params = self.get_search_query_params()
        search_fields = self.prepare_search_fields()
        _queries = []
        for search_field, value in query_params.items():
            if search_field == ALL:
                for field_name_param, field_name \
                        in self.search_args_mapping.items():
                    field_options = copy.copy(search_fields[field_name])
                    field = field_options.pop("field", field_name)

                    if isinstance(value, dict):
                        # For constructions like:
                        # {'title': {'value': 'Produce', 'boost': 1}}
                        _query = value.pop(VALUE)
                        _field_options = copy.copy(value)
                        value = _query
                        field_options.update(_field_options)
                    field_kwargs = {field: {"query": value}}
                    if field_options:
                        field_kwargs[field].update(field_options)
                    # The match query
                    _queries.append(Q(self.query_type, **field_kwargs))
            elif search_field in search_fields:
                field_options = copy.copy(search_fields[search_field])
                field = field_options.pop("field", search_field)

                if isinstance(value, dict):
                    # For constructions like:
                    # {'title': {'value': 'Produce', 'boost': 1}}
                    _query = value.pop(VALUE)
                    _field_options = copy.copy(value)
                    value = _query
                    field_options.update(_field_options)
                field_kwargs = {field: {"query": value}}
                if field_options:
                    field_kwargs[field].update(field_options)
                # The match query
                _queries.append(Q(self.query_type, **field_kwargs))

        return _queries
