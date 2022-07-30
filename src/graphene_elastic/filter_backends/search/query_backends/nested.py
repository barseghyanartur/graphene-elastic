import copy
import operator
import six

from elasticsearch_dsl.query import Q

from ....constants import (
    ALL,
    VALUE,
)
from .base import BaseSearchQueryBackend

__title__ = 'graphene_elastic.filter_backends.search.' \
            'query_backends.nested'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('NestedQueryBackend',)


class NestedQueryBackend(BaseSearchQueryBackend):
    """Nested query backend."""

    query_type = 'nested'

    @property
    def search_fields(self) -> dict:
        return getattr('search_nested_fields', self.search_backend, {})

    def construct_search(self):
        """Construct search.

        Dictionary key is the GET param name. The path option stands for the
        path in Elasticsearch.

        Type 1:

            search_nested_fields = {
                'country': {
                    'path': 'country',
                    'fields': ['name'],
                },
                'city': {
                    'path': 'country.city',
                    'fields': ['name'],
                },
            }

        Type 2:

            search_nested_fields = {
                'country': {
                    'path': 'country',
                    'fields': [{'name': {'boost': 2}}]
                },
                'city': {
                    'path': 'country.city',
                    'fields': [{'name': {'boost': 2}}]
                },
            }

        :return:
        """
        if not self.search_fields:
            return []

        query_params = self.get_search_query_params()
        search_fields = self.prepare_search_fields()
        _queries = []

        for search_field, value in query_params.items():
            if search_field == ALL:
                for field_name_param, field_name \
                        in self.search_args_mapping.items():
                    field_options = copy.copy(search_fields[field_name])
                    field = field_options.pop("field", field_name)
                    path = field_options.get('path')
                    queries = []

                    for _field in field_options.get('fields', []):
                        # In case if we deal with structure 2
                        if isinstance(_field, dict):
                            # TODO: take options (ex: boost) into consideration
                            field = "{}.{}".format(path, _field['name'])
                        # In case if we deal with structure 1
                        else:
                            field = "{}.{}".format(path, _field)

                        # field_kwargs = {
                        #     field: value
                        # }

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
                        queries = [
                            Q("match", **field_kwargs)
                        ]

                    _queries.append(
                        Q(
                            self.query_type,
                            path=path,
                            query=six.moves.reduce(operator.or_, queries)
                        )
                    )
            elif search_field in search_fields:
                field_options = copy.copy(search_fields[search_field])
                field = field_options.pop("field", search_field)
                path = field_options.get('path')
                queries = []

                for _field in field_options.get('fields', []):
                    # In case if we deal with structure 2
                    if isinstance(_field, dict):
                        # TODO: take options (ex: boost) into consideration
                        field = "{}.{}".format(path, _field['name'])
                    # In case if we deal with structure 1
                    else:
                        field = "{}.{}".format(path, _field)

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
                    queries = [
                        Q("match", **field_kwargs)
                    ]

                _queries.append(
                    Q(
                        self.query_type,
                        path=path,
                        query=six.moves.reduce(operator.or_, queries)
                    )
                )

        return _queries
