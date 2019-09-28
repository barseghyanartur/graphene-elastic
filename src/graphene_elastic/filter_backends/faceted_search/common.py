import copy
# from collections import OrderedDict
import enum

from elasticsearch_dsl import TermsFacet
from elasticsearch_dsl.query import Q

import graphene
# from graphene.types import Field

from ...constants import DYNAMIC_CLASS_NAME_PREFIX
from ...helpers import to_pascal_case
from ..base import BaseBackend

__title__ = 'graphene_elastic.filter_backends.faceted_search.common'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'FacetedSearchFilterBackend',
)


def default_agg_field_name_getter(field_name):
    return '_filter_' + field_name


def default_agg_bucket_name_getter(field_name):
    return field_name


class FacetedSearchFilterBackend(BaseBackend):
    """Faceted search filter backend."""

    prefix = 'facets'
    has_connection_fields = True
    has_query_fields = True

    # def get_backend_connection_fields(self):
    #     """Get backend connection fields.
    #
    #     Typical use-case - a backend that alters the Connection object
    #     and adds additional fields next to `edges` and `pageInfo` (see
    #     the `graphene_elastic.relay.connection.Connection` for more
    #     information).
    #
    #     :rtype dict:
    #     :return:
    #     """
    #     from ...types.json_string import JSONString
    #     return OrderedDict([
    #         (
    #             "facets",
    #             Field(
    #                 JSONString,
    #                 name="facets",
    #                 required=False,
    #                 description="Pagination data for this connection.",
    #             ),
    #         ),
    #     ])

    def alter_connection(self, connection, slice):
        """Alter connection object.

        You can add various properties here, returning the altered object.
        Typical use-case would be adding facets to the connection.

        :param connection:
        :param slice:
        :return:
        """
        try:
            connection.facets = slice.aggregations
        except Exception as err:
            connection.facets = {}

    @property
    def faceted_search_fields(self):
        """Faceted search filter fields."""
        search_fields = getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('faceted_search_fields', {})
        return copy.deepcopy(search_fields)

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        return field_name in self.faceted_search_fields

    def get_backend_query_fields(self,
                                 items,
                                 is_filterable_func,
                                 get_type_func):
        """Construct backend filtering fields.

        :param items:
        :param is_filterable_func:
        :param get_type_func:
        :return:
        """
        params = {}
        for field, value in items:
            if is_filterable_func(field):
                # Getting other backend specific fields (schema dependant)
                if self.field_belongs_to(field):
                    params.update({field: field})
        return {
            self.prefix: graphene.Argument(
                graphene.List(
                    graphene.Enum.from_enum(
                        enum.Enum(
                            "{}{}{}BackendEnum".format(
                                DYNAMIC_CLASS_NAME_PREFIX,
                                to_pascal_case(self.prefix),
                                self.connection_field.type.__name__
                            ),
                            params
                        )
                    )
                )
            )
        }

    def prepare_faceted_search_fields(self):
        """Prepare faceted search fields.

        Prepares the following structure:

            >>> {
            >>>     'publisher': {
            >>>         'field': 'publisher.raw',
            >>>         'facet': TermsFacet,
            >>>         'enabled': False,
            >>>     }
            >>>     'date_published': {
            >>>         'field': 'date_published.raw',
            >>>         'facet': DateHistogramFacet,
            >>>         'options': {
            >>>             'interval': 'month',
            >>>         },
            >>>         'enabled': True,
            >>>     },
            >>> }

        :return: Faceted search fields options.
        :rtype: dict
        """
        if not self.faceted_search_fields:
            return {}

        faceted_search_args = dict(self.args).get(self.prefix, [])

        faceted_search_fields = copy.deepcopy(self.faceted_search_fields)

        for field, options in faceted_search_fields.items():
            if options is None or isinstance(options, str):
                faceted_search_fields[field] = {
                    'field': options or field
                }
            elif 'field' not in faceted_search_fields[field]:
                faceted_search_fields[field]['field'] = field

            if 'enabled' in faceted_search_fields[field] \
                    or field in faceted_search_args:
                faceted_search_fields[field]['enabled'] = True
            else:
                faceted_search_fields[field]['enabled'] = False

            if 'facet' not in faceted_search_fields[field]:
                faceted_search_fields[field]['facet'] = TermsFacet

            if 'options' not in faceted_search_fields[field]:
                faceted_search_fields[field]['options'] = {}

            faceted_search_fields[field]['global'] = \
                faceted_search_fields[field].get('global', False)

        return faceted_search_fields

    def get_faceted_search_query_params(self):
        """Get highlight query params.

        :return: List of search query params.
        :rtype: list
        """
        faceted_search_args = dict(self.args).get(self.prefix, {})
        return faceted_search_args

    def construct_facets(self):
        """Construct facets.

        Turns the following structure:

            >>> {
            >>>     'publisher': {
            >>>         'field': 'publisher.raw',
            >>>         'facet': TermsFacet,
            >>>         'enabled': False,
            >>>     }
            >>>     'date_published': {
            >>>         'field': 'date_published',
            >>>         'facet': DateHistogramFacet,
            >>>         'options': {
            >>>             'interval': 'month',
            >>>         },
            >>>         'enabled': True,
            >>>     },
            >>> }

        Into the following structure:

            >>> {
            >>>     'publisher': TermsFacet(field='publisher.raw'),
            >>>     'publishing_frequency': DateHistogramFacet(
            >>>         field='date_published.raw',
            >>>         interval='month'
            >>>     ),
            >>> }
        """
        _facets = {}
        faceted_search_query_params = self.get_faceted_search_query_params()
        faceted_search_fields = self.prepare_faceted_search_fields()
        for _field, _options in faceted_search_fields.items():
            if _field in faceted_search_query_params or _options['enabled']:
                _facets.update(
                    {
                        _field: {
                            'facet': faceted_search_fields[_field]['facet'](
                                field=faceted_search_fields[_field]['field'],
                                **faceted_search_fields[_field]['options']
                            ),
                            'global': faceted_search_fields[_field]['global'],
                        }
                    }
                )
        return _facets

    def aggregate(self,
                  queryset,
                  agg_field_name_getter=default_agg_field_name_getter,
                  agg_bucket_name_getter=default_agg_bucket_name_getter):
        """Aggregate.

        :param queryset:
        :param agg_field_name_getter: callable.
        :param agg_bucket_name_getter:
        :return:
        """
        _facets = self.construct_facets()
        for _field, _facet in _facets.items():
            agg = _facet['facet'].get_aggregation()
            agg_filter = Q('match_all')

            # TODO: Implement
            # for __filter_field, __filter in self._filters.items():
            #     if __field == __filter_field:
            #         continue
            #     agg_filter &= __filter

            if _facet['global']:
                queryset.aggs.bucket(
                    agg_field_name_getter(_field),
                    'global'
                ).bucket(
                    agg_bucket_name_getter(_field),
                    agg
                )
            else:
                queryset.aggs.bucket(
                    agg_field_name_getter(_field),
                    'filter',
                    filter=agg_filter
                ).bucket(
                    agg_bucket_name_getter(_field),
                    agg
                )

        return queryset

    def filter(self, queryset):
        """Filter the queryset.

        :param queryset: Base queryset.
        :type queryset: elasticsearch_dsl.search.Search
        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return self.aggregate(
            queryset,
            agg_field_name_getter=lambda field: field,
            agg_bucket_name_getter=lambda field: 'aggs'
        )
