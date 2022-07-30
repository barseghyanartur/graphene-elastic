from copy import copy, deepcopy
import operator

import graphene
import six

from anysearch.search_dsl.query import Q
from stringcase import pascalcase as to_pascal_case

from ..base import BaseBackend
from ...constants import (
    DYNAMIC_CLASS_NAME_PREFIX,
    ALL,
    VALUE,
    BOOST,
)

__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019-2022 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ("QueryStringBackend",)


class QueryStringBackend(BaseBackend):

    prefix = "query_string"
    has_query_fields = True

    @property
    def query_string_options(self):
        """Query string options.

        Possible options:

            query_string_options = {
                'fields': ['title', 'category', 'tag'],
                'default_operator': "and",
                'lenient': true,
                'minimum_should_match': 3
            }

        For list of all options: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html
        """  # NOQA
        query_string_options = getattr(
            self.connection_field.type._meta.node._meta,
            "filter_backend_options",
            {},
        ).get("query_string_options", {})
        return deepcopy(query_string_options)

    def get_backend_query_fields(
        self, items, is_filterable_func, get_type_func
    ):
        return {self.prefix: graphene.Argument(graphene.String)}

    def get_all_query_params(self):
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return ""
        return filter_args

    def filter(self, queryset):
        """Filter.

        :param queryset:
        :return:
        """

        options = self.query_string_options
        fields = options.pop("fields", [])
        query = self.get_all_query_params()
        if query:
            queryset = queryset.query(
                "query_string",
                query=query,
                fields=fields,
                **options,
            )
        return queryset
