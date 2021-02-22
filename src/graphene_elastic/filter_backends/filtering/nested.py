import operator
from collections import OrderedDict
from copy import deepcopy

import six
from elasticsearch_dsl.query import Q, Query
from stringcase import pascalcase as to_pascal_case

import graphene
from graphene_elastic.filter_backends.filtering.mixins.nested import (
    NestedFilteringFilterMixin,
)
from graphene_elastic.types.json_string import ElasticJSONString

from ...constants import (
    ALL_LOOKUP_FILTERS_AND_QUERIES,
    DYNAMIC_CLASS_NAME_PREFIX,
    LOOKUP_FILTER_EXISTS,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_CONTAINS,
    LOOKUP_QUERY_ENDSWITH,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_ISNULL,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_STARTSWITH,
    VALUE,
)
from .common import FilteringFilterBackend
from .queries import LOOKUP_FILTER_MAPPING

__all__ = ("NestedFilteringFilterBackend",)


def is_nested_field(field):
    return field.type == ElasticJSONString


class NestedFilteringFilterBackend(
    NestedFilteringFilterMixin,
    FilteringFilterBackend
):
    """Nested filter backend."""

    prefix = "nested"
    has_query_fields = True

    @property
    def nested_fields(self):
        """Nested filtering filter fields."""
        nested_filter_fields = getattr(
            self.connection_field.type._meta.node._meta,
            "filter_backend_options",
            {},
        ).get("nested_filter_fields", {})

        return deepcopy(nested_filter_fields)

    def field_belongs_to(self, field_name):
        return field_name in self.nested_fields

    def get_backend_query_fields(
        self, items, is_filterable_func, get_type_func
    ):
        """
        nested: [
            {
                <nested_field_name>: {
                    <property_name>: {
                        ...query filter params
                    }
                }
            }
        ]
        """
        if not self.nested_fields:
            return {}

        params = self.get_backend_default_query_fields_params()
        for field, value in items:
            if is_filterable_func(field) and is_nested_field(value):
                if self.field_belongs_to(field):
                    params[field] = graphene.Argument(
                        type(
                            "{}{}{}{}FilterOptionInput".format(
                                DYNAMIC_CLASS_NAME_PREFIX,
                                to_pascal_case(self.prefix),
                                self.connection_field.type.__name__,
                                to_pascal_case(field),
                            ),
                            (graphene.InputObjectType,),
                            {
                                sub_field: self.get_field_type(
                                    field_name=field,
                                    sub_field_name=sub_field,
                                    field_value=sub_field_value,
                                    base_field_type=None,  # NOTE: 暂时不管
                                )
                                for sub_field, sub_field_value in self.get_field_options(
                                    field
                                ).items()
                            },
                        )
                    )

        return {
            self.prefix: graphene.Argument(
                type(
                    "{}{}{}BackendFilter".format(
                        DYNAMIC_CLASS_NAME_PREFIX,
                        to_pascal_case(self.prefix),
                        self.connection_field.type.__name__,
                    ),
                    (graphene.InputObjectType,),
                    params,
                )
            )
        }

    def get_field_options(self, field_name):
        return self.nested_fields.get(field_name, {})

    def get_sub_field_options(self, field_name, sub_field_name):
        return self.get_field_options(field_name).get(sub_field_name, {})

    def get_field_type(
        self, field_name, sub_field_name, field_value, base_field_type=None
    ):
        """Get field type.

        :return:
        """
        if not self.nested_fields:
            return None

        field_options = self.get_sub_field_options(field_name, sub_field_name)

        if isinstance(field_options, dict) and "lookups" in field_options:
            lookups = field_options.get("lookups", [])
        else:
            lookups = list(ALL_LOOKUP_FILTERS_AND_QUERIES)

        params = (
            OrderedDict({VALUE: base_field_type})
            if base_field_type
            else OrderedDict()
        )
        for lookup in lookups:
            query_cls = LOOKUP_FILTER_MAPPING.get(lookup)
            if not query_cls:
                continue
            params.update({lookup: query_cls()})

        return graphene.Argument(
            type(
                "{}{}{}{}{}".format(
                    DYNAMIC_CLASS_NAME_PREFIX,
                    to_pascal_case(self.prefix),
                    self.connection_field.type.__name__,
                    to_pascal_case(field_name),
                    to_pascal_case(sub_field_name),
                ),
                (graphene.InputObjectType,),
                params,
            )
        )

    @property
    def filter_args_mapping(self):
        return {
            field: list(self.nested_fields[field].keys())
            for field in self.nested_fields
        }

    def prepare_filter_fields(self):
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        filter_fields = {}
        for field, value in filter_args.items():
            sub_fields = self.filter_args_mapping.get(field, None)
            if not sub_fields:
                continue
            for sub_field in sub_fields:
                options = self.get_sub_field_options(field, sub_field)
                if not options and isinstance(options, six.string_types):
                    filter_fields.setdefault(field, {}).update(
                        {
                            sub_field: {
                                "field": options or sub_field,
                                "default_lookup": LOOKUP_FILTER_TERM,
                                "lookups": ALL_LOOKUP_FILTERS_AND_QUERIES,
                            }
                        }
                    )
                elif isinstance(options, dict):
                    filter_fields.setdefault(field, {}).update(
                        {sub_field: options}
                    )

                if "field" not in filter_fields[field][sub_field]:
                    filter_fields[field][sub_field]["field"] = sub_field

                if "default_lookup" not in filter_fields[field][sub_field]:
                    filter_fields[field][sub_field][
                        "default_lookup"
                    ] = LOOKUP_FILTER_TERM

                if "lookups" not in filter_fields[field][sub_field]:
                    filter_fields[field][sub_field][
                        "lookups"
                    ] = ALL_LOOKUP_FILTERS_AND_QUERIES

        return filter_fields

    def get_filter_query_params(self):
        """Get query params to be filtered on.

        We can either specify it like this:

            query_params = {
                'category': {
                    'value': 'Elastic',
                }
            }

        Or using specific lookup:

            query_params = {
                'category': {
                    'term': 'Elastic',
                    'range': {
                        'lower': Decimal('3.0')
                    }
                }
            }

        Note, that `value` would only work on simple types (string, integer,
        decimal). For complex types you would have to use complex param
        anyway. Therefore, it should be forbidden to set `default_lookup` to a
        complex field type.

        Sample values:

            query_params = {
                'category': {
                    'value': 'Elastic',
                }
            }

            filter_fields = {
                'category': {
                    'field': 'category.raw',
                    'default_lookup': 'term',
                    'lookups': (
                        'term',
                        'terms',
                        'range',
                        'exists',
                        'prefix',
                        'wildcard',
                        'contains',
                        'in',
                        'gt',
                        'gte',
                        'lt',
                        'lte',
                        'starts_with',
                        'ends_with',
                        'is_null',
                        'exclude'
                    )
                }
            }

            field_name = 'category'
        """
        query_params = self.prepare_query_params()  # Shall be fixed

        filter_query_params = {}
        filter_fields = self.prepare_filter_fields()  # Correct

        for field_name, field_params in query_params.items():

            if field_name in filter_fields:
                filter_query_params[field_name] = {}

            for sub_field_name, sub_field_params in field_params.items():

                if sub_field_name in filter_fields[field_name]:
                    filter_query_params[field_name][sub_field_name] = []
                    valid_lookups = filter_fields[field_name][sub_field_name][
                        "lookups"
                    ]

                    default_lookup = filter_fields[field_name][
                        sub_field_name
                    ].get("default_lookup", None)

                    for lookup_term, lookup_params in sub_field_params.items():
                        lookup = None

                        if lookup_term == VALUE:
                            if default_lookup:
                                lookup = default_lookup
                        elif lookup_term in valid_lookups:
                            lookup = lookup_term

                        if lookup_params is not None:
                            filter_query_params[field_name][
                                sub_field_name
                            ].append(
                                {
                                    "lookup": lookup,
                                    "path": filter_fields[field_name][
                                        sub_field_name
                                    ].get(
                                        "path", f"{field_name}.{sub_field_name}"
                                    ),
                                    "values": lookup_params,
                                    "field": filter_fields[field_name][
                                        sub_field_name
                                    ].get("field", sub_field_name),
                                    "type": self.doc_type.mapping.properties.name,
                                }
                            )

        return filter_query_params

    def prepare_query_params(self):
        """Prepare query params.

        :return:
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        query_params = {}

        for field, filters in filter_args.items():
            if filters is None:
                continue
            for sub_field, sub_filters in filters.items():
                options = self.get_sub_field_options(field, sub_field)
                if not options:
                    continue
                query_params.setdefault(field, {}).update(
                    {sub_field: sub_filters}
                )
        return query_params

    def filter(self, queryset):
        """Filter."""
        filter_query_params = self.get_filter_query_params()

        for options in filter_query_params.values():

            # For all other cases, when we don't have multiple values,
            # we follow the normal flow.
            for option in options.values():

                for _option in option:
                    if _option["lookup"] == LOOKUP_FILTER_TERMS:
                        queryset = self.apply_filter_terms(
                            queryset, _option, _option["values"]
                        )

                    # `prefix` filter lookup
                    elif _option["lookup"] in (
                        LOOKUP_FILTER_PREFIX,
                        LOOKUP_QUERY_STARTSWITH,
                    ):
                        queryset = self.apply_filter_prefix(
                            queryset, _option, _option["values"]
                        )

                    # `range` filter lookup
                    elif _option["lookup"] == LOOKUP_FILTER_RANGE:
                        queryset = self.apply_filter_range(
                            queryset, _option, _option["values"]
                        )

                    # `exists` filter lookup
                    elif _option["lookup"] == LOOKUP_FILTER_EXISTS:
                        queryset = self.apply_query_exists(
                            queryset, _option, _option["values"]
                        )

                    # `wildcard` filter lookup
                    elif _option["lookup"] == LOOKUP_FILTER_WILDCARD:
                        queryset = self.apply_query_wildcard(
                            queryset, _option, _option["values"]
                        )

                    # `contains` filter lookup
                    elif _option["lookup"] == LOOKUP_QUERY_CONTAINS:
                        queryset = self.apply_query_contains(
                            queryset, _option, _option["values"]
                        )

                    # `in` functional query lookup
                    elif _option["lookup"] == LOOKUP_QUERY_IN:
                        queryset = self.apply_query_in(
                            queryset, _option, _option["values"]
                        )

                    # `gt` functional query lookup
                    elif _option["lookup"] == LOOKUP_QUERY_GT:
                        queryset = self.apply_query_gt(
                            queryset, _option, _option["values"]
                        )

                    # `gte` functional query lookup
                    elif _option["lookup"] == LOOKUP_QUERY_GTE:
                        queryset = self.apply_query_gte(
                            queryset, _option, _option["values"]
                        )

                    # `lt` functional query lookup
                    elif _option["lookup"] == LOOKUP_QUERY_LT:
                        queryset = self.apply_query_lt(
                            queryset, _option, _option["values"]
                        )

                    # `lte` functional query lookup
                    elif _option["lookup"] == LOOKUP_QUERY_LTE:
                        queryset = self.apply_query_lte(
                            queryset, _option, _option["values"]
                        )

                    # `endswith` filter lookup
                    elif _option["lookup"] == LOOKUP_QUERY_ENDSWITH:
                        queryset = self.apply_query_endswith(
                            queryset, _option, _option["values"]
                        )

                    # `isnull` functional query lookup
                    elif _option["lookup"] == LOOKUP_QUERY_ISNULL:
                        queryset = self.apply_query_isnull(
                            queryset, _option, _option["values"]
                        )

                    # `exclude` functional query lookup
                    elif _option["lookup"] == LOOKUP_QUERY_EXCLUDE:
                        queryset = self.apply_query_exclude(
                            queryset, _option, _option["values"]
                        )

                    # `term` filter lookup. This is default if no `default_lookup`
                    # _option has been given or explicit lookup provided.
                    else:
                        queryset = self.apply_filter_term(
                            queryset, _option, _option["values"]
                        )
        return queryset
