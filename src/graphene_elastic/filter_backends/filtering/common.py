import operator
import graphene
from elasticsearch_dsl.query import Q
import six

from ..base import BaseBackend
from ...constants import (
    ALL_LOOKUP_FILTERS_AND_QUERIES,
    DYNAMIC_CLASS_NAME_PREFIX,
    FALSE_VALUES,
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
    TRUE_VALUES,
    VALUE,
    LOWER,
    UPPER,
    GTE,
    LTE,
    BOOST,
)
from .queries import LOOKUP_FILTER_MAPPING

__title__ = "graphene_elastic.filter_backends.filtering.common"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = ("FilteringFilterBackend",)


class FilteringFilterBackend(BaseBackend):
    """Filtering filter backend."""

    prefix = "filter"
    has_fields = True

    @property
    def filter_fields(self):
        """Filtering filter fields."""
        return getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('filter_fields', {})

    @property
    def filter_args_mapping(self):
        return {k: k for k, v in self.filter_fields.items()}

    def field_belongs_to(self, field_name):
        return field_name in self.filter_fields

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
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
                    self.prefix,
                    self.connection_field.type.__name__,
                    field_name.title()
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

    @classmethod
    def get_range_params(cls, value, options):
        """Get params for `range` query.

        Syntax:

            TODO

        Example:

            {
              allPostDocuments(filter:{numViews:{range:{
                    lower:"100",
                    upper:"200",
                    boost:"2.0"
                  }}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param value:
        :param options:
        :type value: str
        :type options: dict
        :return: Params to be used in `range` query.
        :rtype: dict
        """
        if LOWER not in value:
            return {}

        params = {GTE: float(value.get(LOWER, None))}

        if UPPER in value:
            params.update({LTE: float(value.get(UPPER, None))})

        if BOOST in value:
            params.update({BOOST: float(value.get(BOOST, None))})

        return params

    @classmethod
    def get_gte_lte_params(cls, value, lookup, options):
        """Get params for `gte`, `gt`, `lte` and `lt` query.

        Syntax:

            TODO

        Example:

            {
              allPostDocuments(filter:{numViews:{gt:"100", lt:"200"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param value:
        :param lookup:
        :param options:
        :type value: str
        :type lookup: str
        :type options: dict
        :return: Params to be used in `range` query.
        :rtype: dict
        """
        if not value:
            return {}

        params = {lookup: value}

        if BOOST in options:
            params.update({BOOST: float(options.get(BOOST, None))})

        return params

    @classmethod
    def apply_filter_term(cls, queryset, options, value):
        """Apply `term` filter.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{category:{term:"Python"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                    comments
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["term"],
            kwargs={options["field"]: value},
        )

    @classmethod
    def apply_filter_terms(cls, queryset, options, value):
        """Apply `terms` filter.

        Syntax:

            TODO

        Note, that number of values is not limited.

        Example:

        query {
          allPostDocuments(filter:{category:{
                terms:["Python", "Django"]
              }}) {
            edges {
              node {
                category
                title
                content
                numViews
                comments
              }
            }
          }
        }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: mixed: either str or iterable (list, tuple).
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        # If value is a list or a tuple, we use it as is.
        if isinstance(value, (list, tuple)):
            __values = value

        # Otherwise, we consider it to be a string and split it further.
        else:
            __values = cls.split_lookup_complex_value(value)

        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["terms"],
            kwargs={options["field"]: __values},
        )

    @classmethod
    def apply_filter_range(cls, queryset, options, value):
        """Apply `range` filter.

         Syntax:

            TODO

        Example:

            {
              allPostDocuments(filter:{numViews:{range:{
                    lower:"100",
                    upper:"200"
                  }}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }


        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["range"],
            kwargs={
                options["field"]: cls.get_range_params(
                    value,
                    options.get('options', {})
                )
            },
        )

    @classmethod
    def apply_query_exists(cls, queryset, options, value):
        """Apply `exists` filter.

        Syntax:

            TODO

        Example:

            {
              allPostDocuments(filter:{category:{exists:true}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        _value_lower = value  # TODO: clean up?
        if _value_lower in TRUE_VALUES:
            return cls.apply_query(
                queryset=queryset,
                options=options,
                args=[Q("exists", field=options["field"])],
            )
        elif _value_lower in FALSE_VALUES:
            return cls.apply_query(
                queryset=queryset,
                options=options,
                args=[~Q("exists", field=options["field"])],
            )
        return queryset

    @classmethod
    def apply_filter_prefix(cls, queryset, options, value):
        """Apply `prefix` filter.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{category:{prefix:"Pyth"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                    comments
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["prefix"],
            kwargs={options["field"]: value},
        )

    @classmethod
    def apply_query_wildcard(cls, queryset, options, value):
        """Apply `wildcard` filter.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{category:{wildcard:"*ytho*"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                    comments
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_query(
            queryset=queryset,
            options=options,
            args=[Q("wildcard", **{options["field"]: value})],
        )

    @classmethod
    def apply_query_contains(cls, queryset, options, value):
        """Apply `contains` filter.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{category:{contains:"tho"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }


        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_query(
            queryset=queryset,
            options=options,
            args=[Q("wildcard", **{options["field"]: "*{}*".format(value)})],
        )

    @classmethod
    def apply_query_endswith(cls, queryset, options, value):
        """Apply `endswith` filter.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{category:{endsWith:"thon"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_query(
            queryset=queryset,
            options=options,
            args=[Q("wildcard", **{options["field"]: "*{}".format(value)})],
        )

    @classmethod
    def apply_query_in(cls, queryset, options, value):
        """Apply `in` functional query.

        Syntax:

            TODO

        Note, that number of values is not limited.

        Example:

            query {
              allPostDocuments(filter:{tags:{in:["photography", "models"]}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                    tags
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        # If value is a list or a tuple, we use it as is.
        if isinstance(value, (list, tuple)):
            __values = value

        # Otherwise, we consider it to be a string and split it further.
        else:
            __values = cls.split_lookup_complex_value(value)

        __queries = []
        for __value in __values:
            __queries.append(Q("term", **{options["field"]: __value}))

        if __queries:
            queryset = cls.apply_query(
                queryset=queryset,
                options=options,
                args=[six.moves.reduce(operator.or_, __queries)],
            )

        return queryset

    @classmethod
    def apply_query_gt(cls, queryset, options, value):
        """Apply `gt` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{numViews:{gt:"100"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["range"],
            kwargs={
                options["field"]: cls.get_gte_lte_params(
                    value,
                    "gt",
                    options.get('options', {})
                )
            },
        )

    @classmethod
    def apply_query_gte(cls, queryset, options, value):
        """Apply `gte` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{numViews:{gte:"100"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["range"],
            kwargs={
                options["field"]: cls.get_gte_lte_params(
                    value,
                    "gte",
                    options.get('options', {})
                )
            },
        )

    @classmethod
    def apply_query_lt(cls, queryset, options, value):
        """Apply `lt` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{numViews:{lt:"200"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["range"],
            kwargs={
                options["field"]: cls.get_gte_lte_params(
                    value,
                    "lt",
                    options.get('options', {})
                )
            },
        )

    @classmethod
    def apply_query_lte(cls, queryset, options, value):
        """Apply `lte` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{numViews:{lte:"200"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=["range"],
            kwargs={
                options["field"]: cls.get_gte_lte_params(
                    value,
                    "lte",
                    options.get('options', {})
                )
            },
        )

    @classmethod
    def apply_query_isnull(cls, queryset, options, value):
        """Apply `isnull` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{category:{isNull:true}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                    comments
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        _value_lower = value  # TODO: clean up?
        if _value_lower in TRUE_VALUES:
            return cls.apply_query(
                queryset=queryset,
                options=options,
                args=[~Q("exists", field=options["field"])],
            )
        elif _value_lower in FALSE_VALUES:
            return cls.apply_query(
                queryset=queryset,
                options=options,
                args=[Q("exists", field=options["field"])],
            )
        return queryset

    @classmethod
    def apply_query_exclude(cls, queryset, options, value):
        """Apply `exclude` functional query.

        Syntax:

            TODO

        Note, that number of values is not limited.

        Example:

            query {
              allPostDocuments(filter:{category:{exclude:"Python"}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        Or exclude multiple terms at once:

            query {
              allPostDocuments(filter:{category:{exclude:["Ruby", "Java"]}}) {
                edges {
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        if not isinstance(value, (list, tuple)):
            __values = cls.split_lookup_complex_value(value)
        else:
            __values = value

        __queries = []
        for __value in __values:
            __queries.append(~Q("term", **{options["field"]: __value}))

        if __queries:
            queryset = cls.apply_query(
                queryset=queryset,
                options=options,
                args=[six.moves.reduce(operator.and_, __queries)],
            )

        return queryset

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
