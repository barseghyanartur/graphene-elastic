from copy import deepcopy
# from collections import OrderedDict
import enum

from elasticsearch_dsl import TermsFacet
from elasticsearch_dsl.query import Q

import graphene
from stringcase import pascalcase as to_pascal_case
# from graphene.types import Field

from ...constants import DYNAMIC_CLASS_NAME_PREFIX
from ..base import BaseBackend

__title__ = 'graphene_elastic.filter_backends.aggregations.common'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019-2020 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'AggregationsFilterBackend',
)


def default_agg_field_name_getter(field_name):
    return '_filter_' + field_name


def default_agg_bucket_name_getter(field_name):
    return field_name


class AggregationsFilterBackend(BaseBackend):
    """Aggregations search filter backend."""

    prefix = 'aggregations'
    has_connection_fields = True
    has_query_fields = True

    def alter_connection(self, connection, slice):
        """Alter connection object.

        You can add various properties here, returning the altered object.
        Typical use-case would be adding facets to the connection.

        :param connection:
        :param slice:
        :return:
        """
        try:
            connection.aggregations = slice.aggregations
        except Exception as err:
            connection.aggregations = {}

    @property
    def aggregations_fields(self):
        """Faceted search filter fields."""
        search_fields = getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('aggregations_fields', {})
        return deepcopy(search_fields)

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        return field_name in self.aggregations_fields

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

    def prepare_aggregations_fields(self):
        """Prepare faceted search fields.

        Goal:

            "aggs": {
                "my_unbiased_sample": {
                  "diversified_sampler": {
                    "shard_size": 200,
                    "field": "tags.keyword"
                  },
                  "aggs": {
                    "keywords": {
                      "significant_text": {
                        "field": "content"
                      }
                    }
                  }
                }
              }

        Python code:

            s = Search()
            s.aggs.bucket(
                'my_unbiased_sample',
                agg_type='diversified_sampler',
                field='tags.keyword',
                shard_size=200
            ).bucket(
                'keywords',
                agg_type='significant_text',
                field='content'
            )

        Definition:

            aggregations_fields = {
                "my_unbiased_sample": [
                    {
                        "name": "my_unbiased_sample",
                        "type": "bucket",
                        "agg_type": "diversified_sampler",
                        "args": {
                            "shard_size": 200,
                            "field": "tags.keyword",
                        },
                    },
                    {
                        "name": "keywords",
                        "type": "bucket",
                        "agg_type": "significant_text",
                        "args": {
                            "field": "content",
                        },
                    },
                ]
            }

        :return: Faceted search fields options.
        :rtype: dict
        """
        if not self.aggregations_fields:
            return {}

        aggregations_args = dict(self.args).get(self.prefix, [])

        aggregations_fields = deepcopy(self.aggregations_fields)

        for field, options in aggregations_fields.items():
            if options is None or isinstance(options, str):
                aggregations_fields[field] = {
                    'field': options or field
                }
            elif 'field' not in aggregations_fields[field]:
                aggregations_fields[field]['field'] = field

            if 'enabled' in aggregations_fields[field] \
                    or field in aggregations_args:
                aggregations_fields[field]['enabled'] = True
            else:
                aggregations_fields[field]['enabled'] = False

            if 'facet' not in aggregations_fields[field]:
                aggregations_fields[field]['facet'] = TermsFacet

            if 'options' not in aggregations_fields[field]:
                aggregations_fields[field]['options'] = {}

            aggregations_fields[field]['global'] = \
                aggregations_fields[field].get('global', False)

        return aggregations_fields

    def get_aggregations_query_params(self):
        """Get highlight query params.

        :return: List of search query params.
        :rtype: list
        """
        aggregations_args = dict(self.args).get(self.prefix, {})
        return aggregations_args

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
        _aggs = {}
        aggregations_query_params = self.get_aggregations_query_params()
        aggregations_fields = self.prepare_aggregations_fields()
        for _field, _options in aggregations_fields.items():
            if _field in aggregations_query_params or _options['enabled']:
                _aggs.update(
                    {
                        _field: {
                            'facet': aggregations_fields[_field]['facet'](
                                field=aggregations_fields[_field]['field'],
                                **aggregations_fields[_field]['options']
                            ),
                            'global': aggregations_fields[_field]['global'],
                        }
                    }
                )
        return _aggs

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
        _aggs = self.construct_facets()
        for _field, _agg in _aggs.items():
            agg = _agg['facet'].get_aggregation()
            agg_filter = Q('match_all')

            # TODO: Implement
            # for __filter_field, __filter in self._filters.items():
            #     if __field == __filter_field:
            #         continue
            #     agg_filter &= __filter

            if _agg['global']:
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
