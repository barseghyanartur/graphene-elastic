from typing import Callable
import operator
from anysearch.search_dsl.query import Q
import six

from graphene_elastic.constants import (
    FALSE_VALUES,
    TRUE_VALUES,
    LOWER,
    UPPER,
    GTE,
    LTE,
    BOOST,
)

__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019-2022 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'FilteringFilterMixin',
)


def q_params(lookup, options, query=None):
    if query is None:
        query = {options["field"]: options["values"]}

    if options.get("path"):
        # Nested query
        return Q("nested", query={lookup: query}, path=options["path"])
    return Q(lookup, **query)


class FilteringFilterMixin(object):
    """Filtering filter mixin."""

    apply_query: Callable
    apply_filter: Callable
    split_lookup_complex_value: Callable

    @classmethod
    def get_range_param_value(cls, value):
        """Get range param value.

        :param value:
        :type value:
            graphene_elastic.filter_backends.filtering.queries.InputObjectType
        :return:
        """
        if not value:
            return None

        return (
            value.decimal
            or value.float
            or value.int
            or value.date
            or value.datetime
        )

    @classmethod
    def get_range_params(cls, value, options):
        """Get params for `range` query.

        Syntax:

            TODO

        Example:

            {
              allPostDocuments(filter:{numViews:{range:{
                    lower:{decimal:"100"},
                    upper:{decimal: "200"},
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
        :type value:
            graphene_elastic.filter_backends.filtering.queries.InputObjectType
        :type options: dict
        :return: Params to be used in `range` query.
        :rtype: dict
        """
        if LOWER not in value:
            return {}

        params = {GTE: cls.get_range_param_value(value.get(LOWER, None))}

        if UPPER in value:
            params.update({
                LTE: cls.get_range_param_value(value.get(UPPER, None))
            })

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
              allPostDocuments(filter:{numViews:{
                    gt:{decimal:"100"},
                    lt:{decimal:"200"}
                }}) {
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
        :type value:
            graphene_elastic.filter_backends.filtering.queries.InputObjectType
        :type lookup: str
        :type options: dict
        :return: Params to be used in `range` query.
        :rtype: dict
        """
        if not value:
            return {}

        _value = cls.get_range_param_value(value)

        if not _value:
            return {}

        params = {lookup: _value}

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

        q = q_params("term", options)
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=[q],
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

        q = q_params("terms", options, {options["field"]: __values})

        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=[q]
        )

    @classmethod
    def apply_filter_range(cls, queryset, options, value):
        """Apply `range` filter.

         Syntax:

            TODO

        Example:

            {
              allPostDocuments(filter:{numViews:{range:{
                    lower:{decimal:"100"},
                    upper:{decimal:"200"}
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
        q = q_params("range", options, {options["field"]: cls.get_range_params(
            value,
            options.get('options', {})
        )})

        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=[q]
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
        q = q_params("exists", options, query={"field": options["field"]})
        if _value_lower in TRUE_VALUES:
            return cls.apply_query(
                queryset=queryset,
                options=options,
                args=[q],
            )
        elif _value_lower in FALSE_VALUES:
            return cls.apply_query(
                queryset=queryset,
                options=options,
                args=[~q],
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
        q = q_params("prefix", options)

        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=[q],
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
        q = q_params("wildcard", options)

        return cls.apply_query(
            queryset=queryset,
            options=options,
            args=[q],
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
        q = q_params("wildcard", options, query={
                    options["field"]: "*{}*".format(value)})

        return cls.apply_query(
            queryset=queryset,
            options=options,
            args=[q],
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
        q = q_params("wildcard", options, query={
                    options["field"]: "*{}".format(value)})

        return cls.apply_query(
            queryset=queryset,
            options=options,
            args=[q],
        )

    @classmethod
    def apply_query_in(cls, queryset, options, value):
        """Apply `in` functional query.

        Syntax:

            TODO

        Note, that number of values is not limited.

        Example:

            query {
              allPostDocuments(postFilter:{tags:{
                    in:["photography", "models"]
                }}) {
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
            _values = value

        # Otherwise, we consider it to be a string and split it further.
        else:
            _values = cls.split_lookup_complex_value(value)

        _queries = []
        for _value in _values:
            _queries.append(q_params("term", options, query={
                            options["field"]: _value}))

        if _queries:
            queryset = cls.apply_query(
                queryset=queryset,
                options=options,
                args=[six.moves.reduce(operator.or_, _queries)],
            )

        return queryset

    @classmethod
    def apply_query_gt(cls, queryset, options, value):
        """Apply `gt` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{numViews:{
                    gt:{decimal:"100"}
                }}) {
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
        q = q_params(
            "range",
            options,
            {
                options["field"]: cls.get_gte_lte_params(
                    value,
                    "gt",
                    options.get("options", {})
                )
            }
        )
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=[q]
        )

    @classmethod
    def apply_query_gte(cls, queryset, options, value):
        """Apply `gte` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{numViews:{
                    gte:{decimal:"100"}
                }}) {
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
        q = q_params(
            "range",
            options,
            {
                options["field"]: cls.get_gte_lte_params(
                    value,
                    "gte",
                    options.get("options", {})
                )
            }
        )
        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=[q]
        )

    @classmethod
    def apply_query_lt(cls, queryset, options, value):
        """Apply `lt` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{numViews:{
                    lt:{decimal:"200"}
                }}) {
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
        q = q_params(
            "range",
            options,
            {
                options["field"]: cls.get_gte_lte_params(
                    value,
                    "lt",
                    options.get("options", {})
                )
            }
        )

        return cls.apply_filter(
            queryset=queryset,
            options=options,
            args=[q]
        )

    @classmethod
    def apply_query_lte(cls, queryset, options, value):
        """Apply `lte` functional query.

        Syntax:

            TODO

        Example:

            query {
              allPostDocuments(filter:{numViews:{
                    lte:{decimal:"200"}
                }}) {
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
        q = q_params(
            "range",
            options,
            {
                options["field"]: cls.get_gte_lte_params(
                    value,
                    "lt",
                    options.get("options", {})
                )
            }
        )

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
        q = q_params("exists", options, query={"field": options["field"]})

        if _value_lower in TRUE_VALUES:
            return cls.apply_query(
                queryset=queryset,
                options=options,
                args=[~q],
            )
        elif _value_lower in FALSE_VALUES:
            return cls.apply_query(
                queryset=queryset,
                options=options,
                args=[q],
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
            __queries.append(~q_params("term", options, query={
                             options["field"]: __value}))

        if __queries:
            queryset = cls.apply_query(
                queryset=queryset,
                options=options,
                args=[six.moves.reduce(operator.and_, __queries)],
            )

        return queryset
