import copy

from elasticsearch_dsl.query import Q
import six

from ....constants import (
    ALL,
    VALUE,
)
from .base import BaseSearchQueryBackend

__title__ = 'graphene_elastic.filter_backends.search.query_backends.match'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('MatchQueryBackend',)


class MatchQueryBackend(BaseSearchQueryBackend):
    """Match query backend."""

    query_type = 'match'

    @classmethod
    def prepare_search_fields(self):
        """Prepare search fields.

        Possible structures:

            search_fields = {
                'title': {'boost': 4, 'field': 'title.raw'},
                'content': {'boost': 2},
                'category': None,
            }

        We shall finally have:

            search_fields = {
                'title': {
                    'field': 'title.raw',
                    'boost': 4
                },
                'content': {
                    'field': 'content',
                    'boost': 2
                },
                'category': {
                    'field': 'category'
                }
            }

        Sample query would be:

            {
              allPostDocuments(search:{query:"Another"}) {
                pageInfo {
                  startCursor
                  endCursor
                  hasNextPage
                  hasPreviousPage
                }
                edges {
                  cursor
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }


        :return: Filtering options.
        :rtype: dict
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        filter_fields = {}

        # {'query': '', 'title': {'query': '', 'boost': 1}}

        for field, _ in self.search_args_mapping.items():
            filter_fields.update({field: {}})
            options = self.search_fields.get(field)
            # For constructions like 'category': 'category.raw' we shall
            # have the following:
            #
            if options is None or isinstance(options, six.string_types):
                filter_fields.update(
                    {
                        field: {"field": options or field}
                    }
                )
            elif "field" not in options:
                filter_fields.update({field: options})
                filter_fields[field]["field"] = field
            else:
                filter_fields.update({field: options})

        return filter_fields

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
        # __queries = []
        # for search_term in query_params.items():
        #     __values = search_backend.split_lookup_name(search_term, 1)
        #     __len_values = len(__values)
        #     if __len_values > 1:
        #         field, value = __values
        #         if field in view.search_fields:
        #             # Initial kwargs for the match query
        #             field_kwargs = {field: {'query': value}}
        #             # In case if we deal with structure 2
        #             if isinstance(view.search_fields, dict):
        #                 extra_field_kwargs = view.search_fields[field]
        #                 if extra_field_kwargs:
        #                     field_kwargs[field].update(extra_field_kwargs)
        #             # The match query
        #             __queries.append(
        #                 Q(cls.query_type, **field_kwargs)
        #             )
        #     else:
        #         for field in view.search_fields:
        #             # Initial kwargs for the match query
        #             field_kwargs = {field: {'query': search_term}}
        #
        #             # In case if we deal with structure 2
        #             if isinstance(view.search_fields, dict):
        #                 extra_field_kwargs = view.search_fields[field]
        #                 if extra_field_kwargs:
        #                     field_kwargs[field].update(extra_field_kwargs)
        #
        #             # The match query
        #             __queries.append(
        #                 Q(cls.query_type, **field_kwargs)
        #             )
        # return __queries
