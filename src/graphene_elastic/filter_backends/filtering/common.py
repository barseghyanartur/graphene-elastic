import copy
import graphene
import six

from ..base import BaseBackend
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
from ...helpers import to_pascal_case
from .queries import LOOKUP_FILTER_MAPPING
from .mixins import FilteringFilterMixin

__title__ = "graphene_elastic.filter_backends.filtering.common"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = ("FilteringFilterBackend",)


class FilteringFilterBackend(BaseBackend, FilteringFilterMixin):
    """Filtering filter backend."""

    prefix = "filter"
    has_query_fields = True

    @property
    def filter_fields(self):
        """Filtering filter fields."""
        filter_fields = getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('filter_fields', {})

        return copy.deepcopy(filter_fields)

    @property
    def filter_args_mapping(self):
        return {field: field for field, value in self.filter_fields.items()}

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        return field_name in self.filter_fields

    def get_backend_query_fields(self,
                                 items,
                                 is_filterable_func,
                                 get_type_func):
        """Fail proof override.

        :param items:
        :param is_filterable_func:
        :param get_type_func:
        :return:
        """
        if not self.filter_fields:
            return {}

        return super(FilteringFilterBackend, self).get_backend_query_fields(
            items=items,
            is_filterable_func=is_filterable_func,
            get_type_func=get_type_func
        )

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
        if not self.filter_fields:
            return None

        field_options = self.get_field_options(field_name)
        if isinstance(field_options, dict) and "lookups" in field_options:
            lookups = field_options.get("lookups", [])
        else:
            lookups = list(ALL_LOOKUP_FILTERS_AND_QUERIES)

        params = {VALUE: base_field_type}
        for lookup in lookups:
            query_cls = LOOKUP_FILTER_MAPPING.get(lookup)
            if not query_cls:
                continue
            params.update({lookup: query_cls()})

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

    # def get_field_options(self, field_name):
    #     """Get field options."""
    #     if field_name in self.filter_fields:
    #         return self.filter_fields[field_name]
    #     return {}

    def prepare_filter_fields(self):
        """Prepare filter fields.

        Possible structures:

            filter_fields = {
                'title': {
                    'field': 'title.raw',
                    'lookups': [
                        LOOKUP_FILTER_TERM,
                        LOOKUP_FILTER_TERMS,
                        LOOKUP_FILTER_PREFIX,
                        LOOKUP_FILTER_WILDCARD,
                        LOOKUP_QUERY_IN,
                        LOOKUP_QUERY_EXCLUDE,
                    ],
                    'default_lookup': LOOKUP_FILTER_TERM,
                },
                'category': 'category.raw',
            }

        We shall finally have:

            filter_fields = {
                'title': {
                    'field': 'title.raw',
                    'lookups': [
                        LOOKUP_FILTER_TERM,
                        LOOKUP_FILTER_TERMS,
                        LOOKUP_FILTER_PREFIX,
                        LOOKUP_FILTER_WILDCARD,
                        LOOKUP_QUERY_IN,
                        LOOKUP_QUERY_EXCLUDE,
                    ],
                    'default_lookup': LOOKUP_FILTER_TERM,
                },
                'category': {
                    'field': 'category.raw',
                    'lookups': [
                        LOOKUP_FILTER_TERM,
                        LOOKUP_FILTER_TERMS,
                        LOOKUP_FILTER_PREFIX,
                        LOOKUP_FILTER_WILDCARD,
                        LOOKUP_QUERY_IN,
                        LOOKUP_QUERY_EXCLUDE,
                        ...
                        # All other lookups
                    ],
                    'default_lookup': LOOKUP_FILTER_TERM,
                }
            }
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        filter_fields = {}

        for arg, value in filter_args.items():
            field = self.filter_args_mapping.get(arg, None)
            if field is None:
                continue
            filter_fields.update({field: {}})
            options = self.filter_fields.get(field)
            # For constructions like 'category': 'category.raw' we shall
            # have the following:
            # TODO: Make sure to use custom (user specified) lookups
            if options is None or isinstance(options, six.string_types):
                filter_fields.update(
                    {
                        field: {
                            "field": options or field,
                            "default_lookup": LOOKUP_FILTER_TERM,
                            "lookups": tuple(ALL_LOOKUP_FILTERS_AND_QUERIES),
                        }
                    }
                )
            elif "field" not in options:
                filter_fields.update({field: options})
                filter_fields[field]["field"] = field
            else:
                filter_fields.update({field: options})

            if (
                field in filter_fields
                and "lookups" not in filter_fields[field]
            ):
                filter_fields[field].update(
                    {"lookups": tuple(ALL_LOOKUP_FILTERS_AND_QUERIES)}
                )
        return filter_fields

    def prepare_query_params(self):
        """Prepare query params.

        :return:
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        query_params = {}

        for arg, filters in filter_args.items():
            field = self.filter_args_mapping.get(arg, None)
            if field is None:
                continue
            query_params[field] = filters
        return query_params

    def get_field_lookup_param(self, field_name):
        """Get field lookup param.

        :param field_name:
        :return:
        """
        field_options = dict(self.args) \
            .get(self.prefix, {}) \
            .get(field_name, {})
        return field_options.get("lookup", None)

    def get_field_options(self, field_name):
        """Get field option params.

        :param field_name:
        :return:
        """
        return dict(self.args).get(self.prefix, {}).get(field_name, {})

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

        for field_name, lookup_params in query_params.items():

            if field_name in filter_fields:
                filter_query_params[field_name] = []
                valid_lookups = filter_fields[field_name]["lookups"]

                # If we have default lookup given use it as a default and
                # do not require further suffix specification.
                default_lookup = None
                if "default_lookup" in filter_fields[field_name]:
                    default_lookup = \
                        filter_fields[field_name]["default_lookup"]

                for lookup_param, lookup_options in lookup_params.items():
                    lookup = None
                    if lookup_param == VALUE:
                        if default_lookup is not None:
                            lookup = default_lookup
                    elif lookup_param in valid_lookups:
                        lookup = lookup_param

                    if lookup_options is not None:
                        filter_query_params[field_name].append({
                            "lookup": lookup,
                            "values": lookup_options,
                            "field": filter_fields[field_name].get(
                                "field", field_name
                            ),
                            "type": self.doc_type.mapping.properties.name,
                        })
        return filter_query_params

    def filter(self, queryset):
        """Filter."""
        filter_query_params = self.get_filter_query_params()

        for options in filter_query_params.values():

            # For all other cases, when we don't have multiple values,
            # we follow the normal flow.
            for option in options:

                if option["lookup"] == LOOKUP_FILTER_TERMS:
                    queryset = self.apply_filter_terms(
                        queryset,
                        option,
                        option['values']
                    )

                # `prefix` filter lookup
                elif option["lookup"] in (
                    LOOKUP_FILTER_PREFIX,
                    LOOKUP_QUERY_STARTSWITH,
                ):
                    queryset = self.apply_filter_prefix(
                        queryset,
                        option,
                        option['values']
                    )

                # `range` filter lookup
                elif option["lookup"] == LOOKUP_FILTER_RANGE:
                    queryset = self.apply_filter_range(
                        queryset,
                        option,
                        option['values']
                    )

                # `exists` filter lookup
                elif option["lookup"] == LOOKUP_FILTER_EXISTS:
                    queryset = self.apply_query_exists(
                        queryset,
                        option,
                        option['values']
                    )

                # `wildcard` filter lookup
                elif option["lookup"] == LOOKUP_FILTER_WILDCARD:
                    queryset = self.apply_query_wildcard(
                        queryset,
                        option,
                        option['values']
                    )

                # `contains` filter lookup
                elif option["lookup"] == LOOKUP_QUERY_CONTAINS:
                    queryset = self.apply_query_contains(
                        queryset,
                        option,
                        option['values']
                    )

                # `in` functional query lookup
                elif option["lookup"] == LOOKUP_QUERY_IN:
                    queryset = self.apply_query_in(
                        queryset,
                        option,
                        option['values']
                    )

                # `gt` functional query lookup
                elif option["lookup"] == LOOKUP_QUERY_GT:
                    queryset = self.apply_query_gt(
                        queryset,
                        option,
                        option['values']
                    )

                # `gte` functional query lookup
                elif option["lookup"] == LOOKUP_QUERY_GTE:
                    queryset = self.apply_query_gte(
                        queryset,
                        option,
                        option['values']
                    )

                # `lt` functional query lookup
                elif option["lookup"] == LOOKUP_QUERY_LT:
                    queryset = self.apply_query_lt(
                        queryset,
                        option,
                        option['values']
                    )

                # `lte` functional query lookup
                elif option["lookup"] == LOOKUP_QUERY_LTE:
                    queryset = self.apply_query_lte(
                        queryset,
                        option,
                        option['values']
                    )

                # `endswith` filter lookup
                elif option["lookup"] == LOOKUP_QUERY_ENDSWITH:
                    queryset = self.apply_query_endswith(
                        queryset,
                        option,
                        option['values']
                    )

                # `isnull` functional query lookup
                elif option["lookup"] == LOOKUP_QUERY_ISNULL:
                    queryset = self.apply_query_isnull(
                        queryset,
                        option,
                        option['values']
                    )

                # `exclude` functional query lookup
                elif option["lookup"] == LOOKUP_QUERY_EXCLUDE:
                    queryset = self.apply_query_exclude(
                        queryset,
                        option,
                        option['values']
                    )

                # `term` filter lookup. This is default if no `default_lookup`
                # option has been given or explicit lookup provided.
                else:
                    queryset = self.apply_filter_term(
                        queryset,
                        option,
                        option['values']
                    )

        return queryset
