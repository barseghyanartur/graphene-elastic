import copy
import operator

import graphene
import six

from elasticsearch_dsl.query import Q

from ..base import BaseBackend
from ...constants import (
    DYNAMIC_CLASS_NAME_PREFIX,
    STRING_LOOKUP_FILTERS,
    EXTENDED_STRING_LOOKUP_FILTERS,
    NUMBER_LOOKUP_FILTERS,
    EXTENDED_NUMBER_LOOKUP_FILTERS,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_QUERY_STARTSWITH,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_EXISTS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_CONTAINS,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_ENDSWITH,
    LOOKUP_QUERY_ISNULL,
    LOOKUP_QUERY_EXCLUDE,
    ALL_LOOKUP_FILTERS_AND_QUERIES,
    TRUE_VALUES,
    FALSE_VALUES,
    ALL,
    VALUE,
    BOOST,
)

__title__ = 'graphene_elastic.filter_backends.search.common'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL-2.0-only OR LGPL-2.1-or-later'
__all__ = (
    'SearchFilterBackend',
)


class SearchFilterBackend(BaseBackend):
    prefix = 'search'

    def field_belongs_to(self, field_name):
        return field_name in self.connection_field.search_fields

    def get_field_options(self, field_name):
        """"""
        if field_name in self.connection_field.search_fields:
            return self.connection_field.search_fields[field_name]
        return {}

    def get_backend_default_fields_params(self):
        """Get backend default filter params.

        :rtype: dict
        :return:
        """
        return {ALL: graphene.String()}

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
        # return base_field_type
        params = {
            VALUE: base_field_type,  # Value to search on. Required.
            BOOST: graphene.Int(),  # Boost the given field with. Optional.
        }
        return graphene.Argument(
            type(
                '{}{}{}'.format(
                    DYNAMIC_CLASS_NAME_PREFIX,
                    self.prefix,
                    field_name.title()
                ),
                (graphene.InputObjectType,),
                params
            )
        )

    @classmethod
    def generic_fields(cls):
        """Generic backend specific fields.

        :return:
        """
        return {cls.prefix: graphene.String()}

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

        :param view:
        :type view: rest_framework.viewsets.ReadOnlyModelViewSet
        :return: Filtering options.
        :rtype: dict
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        filter_fields = {}

        # {'query': '', 'title': {'query': '', 'boost': 1}}

        for arg, value in filter_args.items():
            field = self.connection_field.search_args_mapping.get(arg, None)
            if field is None:
                continue
            filter_fields.update({field: {}})
            options = self.connection_field.search_fields.get(field)
            # For constructions like 'category': 'category.raw' we shall
            # have the following:
            #
            if options is None or isinstance(options, six.string_types):
                filter_fields.update(
                    {
                        field: {
                            'field': options or field,
                            # 'default_lookup': LOOKUP_FILTER_TERM,
                            # 'lookups': tuple(ALL_LOOKUP_FILTERS_AND_QUERIES)
                        }
                    }
                )
            elif 'field' not in options:
                filter_fields.update({field: options})
                filter_fields[field]['field'] = field
            else:
                filter_fields.update({field: options})

            # if field in filter_fields and 'lookups' not in filter_fields[field]:
            #     filter_fields[field].update(
            #         {
            #             'lookups': tuple(ALL_LOOKUP_FILTERS_AND_QUERIES)
            #         }
            #     )
        return filter_fields

    def prepare_query_params(self):
        """

        :return:
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        query_params = {}
        for arg, value in filter_args.items():
            field = self.connection_field.search_args_mapping.get(arg, None)
            if field is None:
                continue
            query_params[field] = value
        return query_params

    def get_filter_query_params(self):
        """Get query params to be filtered on.

        :param request: Django REST framework request.
        :param view: View.
        :type request: rest_framework.request.Request
        :type view: rest_framework.viewsets.ReadOnlyModelViewSet
        :return: Request query params to filter on.
        :rtype: dict
        """
        query_params = self.prepare_query_params()

        filter_query_params = {}
        filter_fields = self.prepare_search_fields()

        for field_name, values in query_params.items():
            query_param_list = self.split_lookup_filter(
                field_name,
                maxsplit=1
            )
            # field_name = query_param_list[0]

            if field_name in filter_fields:
                lookup_param = None
                if len(query_param_list) > 1:
                    lookup_param = query_param_list[1]

                valid_lookups = filter_fields[field_name]['lookups']

                # If we have default lookup given use it as a default and
                # do not require further suffix specification.
                default_lookup = None
                if 'default_lookup' in filter_fields[field_name]:
                    default_lookup = \
                        filter_fields[field_name]['default_lookup']

                if lookup_param is None or lookup_param in valid_lookups:

                    # If we have default lookup given use it as a default
                    # and do not require further suffix specification.
                    if lookup_param is None and default_lookup is not None:
                        lookup_param = str(default_lookup)

                    if isinstance(values, (list, tuple)):
                        values = [
                            __value.strip()
                            for __value
                            in values
                            if __value.strip() != ''
                        ]
                    else:
                        values = [values]

                    if values:
                        filter_query_params[field_name] = {
                            'lookup': lookup_param,
                            'values': values,
                            'field': filter_fields[field_name].get(
                                'field',
                                field_name
                            ),
                            'type': self.connection_field.document._doc_type \
                                        .mapping.properties.name
                        }
        return filter_query_params

    def construct_search(self):
        """Construct search.

        We have to deal with two types of structures:

        Type 1:

        >>> search_fields = (
        >>>     'title',
        >>>     'description',
        >>>     'summary',
        >>> )

        Type 2:

        >>> search_fields = {
        >>>     'title': {'field': 'title', 'boost': 2},
        >>>     'description': None,
        >>>     'summary': None,
        >>> }

        In REST it was:

            /search/books/?search=education
            /search/books/?search=title:education&search=summary:technology

        In GraphQL shall be:

            query PostsQuery {
              allPostDocuments(
                    searchTitle: "education",
                    searchSummary: "technology"
                ) {
                edges {
                  node {
                    id
                    title
                    category
                    content
                    createdAt
                    comments
                  }
                }
              }
            }

        Or simply:

            query PostsQuery {
              allPostDocuments(search: "education technology") {
                edges {
                  node {
                    id
                    title
                    category
                    content
                    createdAt
                    comments
                  }
                }
              }
            }


        :param request: Django REST framework request.
        :param queryset: Base queryset.
        :param view: View.
        :type request: rest_framework.request.Request
        :type queryset: elasticsearch_dsl.search.Search
        :type view: rest_framework.viewsets.ReadOnlyModelViewSet
        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """

        query_params = self.prepare_query_params()

        search_query_params = {}
        search_fields = self.prepare_search_fields()
        _queries = []
        for search_field, value in query_params.items():
            search_parts = self.split_lookup_name(search_field, maxsplit=1)
            _len_values = len(search_parts)
            if len(search_parts) > 1:
                field_name = search_parts[0]
                lookup_param = search_parts[1]
            else:
                field_name = search_parts[0]
                lookup_param = None

            if field_name in search_fields:
                field_options = copy.copy(search_fields[field_name])
                field = field_options.pop('field', field_name)

                if isinstance(value, dict):
                    # For constructions like:
                    # {'title': {'query': 'Produce', 'boost': 1}}
                    _query = value.pop('query')
                    _field_options = copy.copy(value)
                    value = _query
                    field_options.update(_field_options)
                field_kwargs = {field: {'query': value}}
                if field_options:
                    field_kwargs[field].update(field_options)
                # The match query
                _queries.append(
                    Q("match", **field_kwargs)
                )

        return _queries

    def construct_nested_search(self):
        """Construct nested search.

        We have to deal with two types of structures:

        Type 1:

        >>> search_nested_fields = {
        >>>     'country': {
        >>>         'path': 'country',
        >>>         'fields': ['name'],
        >>>     },
        >>>     'city': {
        >>>         'path': 'country.city',
        >>>         'fields': ['name'],
        >>>     },
        >>> }

        Type 2:

        >>> search_nested_fields = {
        >>>     'country': {
        >>>         'path': 'country',
        >>>         'fields': [{'name': {'boost': 2}}]
        >>>     },
        >>>     'city': {
        >>>         'path': 'country.city',
        >>>         'fields': [{'name': {'boost': 2}}]
        >>>     },
        >>> }

        :param request: Django REST framework request.
        :param queryset: Base queryset.
        :param view: View.
        :type request: rest_framework.request.Request
        :type queryset: elasticsearch_dsl.search.Search
        :type view: rest_framework.viewsets.ReadOnlyModelViewSet
        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        if not hasattr(self, 'search_nested_fields') \
                or not self.search_nested_fields:
            return []

        # TODO: Support query boosting

        query_params = self.prepare_search_fields()
        __queries = []
        for search_term in query_params:
            for label, options in self.search_nested_fields.items():
                queries = []
                path = options.get('path')

                for _field in options.get('fields', []):

                    # In case if we deal with structure 2
                    if isinstance(_field, dict):
                        # TODO: take options (such as boost) into consideration
                        field = "{}.{}".format(path, _field['name'])
                    # In case if we deal with structure 1
                    else:
                        field = "{}.{}".format(path, _field)

                    field_kwargs = {
                        field: search_term
                    }

                    queries.append(
                        Q("match", **field_kwargs)
                    )

                __queries.append(
                    Q(
                        "nested",
                        path=path,
                        query=six.moves.reduce(operator.or_, queries)
                    )
                )

        return __queries

    def filter(self, queryset):

        # return queryset

        # TODO
        # _queries = self.construct_search() + []
        _queries = self.construct_search() + self.construct_nested_search()

        if _queries:
            queryset = queryset.query('bool', should=_queries)
        return queryset