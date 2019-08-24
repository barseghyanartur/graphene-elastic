import copy
import operator
import graphene
from elasticsearch_dsl.query import Q
import six

from ..base import BaseBackend
from ...constants import (
    ALL,
    ALL_LOOKUP_FILTERS_AND_QUERIES,
    BOOST,
    DYNAMIC_CLASS_NAME_PREFIX,
    EXTENDED_NUMBER_LOOKUP_FILTERS,
    EXTENDED_STRING_LOOKUP_FILTERS,
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
    NUMBER_LOOKUP_FILTERS,
    STRING_LOOKUP_FILTERS,
    TRUE_VALUES,
    VALUE,
    FIELD,
    LOOKUP,
)
from ...enums import NoValue, convert_list_to_enum

__title__ = "graphene_elastic.filter_backends.filtering.common"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = ("FilteringFilterBackend",)


class FilteringFilterBackend(BaseBackend):
    prefix = "filter"

    def field_belongs_to(self, field_name):
        return field_name in self.connection_field.filter_fields

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
        lookups = []
        field_options = self.get_field_options(field_name)
        if isinstance(field_options, dict) and "lookups" in field_options:
            lookups = field_options.get("lookups", [])
        else:
            lookups = list(ALL_LOOKUP_FILTERS_AND_QUERIES)
        params = {
            # FIELD: graphene.String(),  # Field to filter on. Required.
            # TODO: The line below shall relay to the ``base_field_type``
            # and not just a ``graphene.String``
            VALUE: graphene.List(
                graphene.String
            )  # Value to filter on. Required.
        }
        if lookups:
            params.update(
                {
                    LOOKUP: graphene.Field(
                        graphene.Enum.from_enum(
                            convert_list_to_enum(
                                lookups,
                                enum_name="{}{}{}Enum".format(
                                    DYNAMIC_CLASS_NAME_PREFIX,
                                    self.prefix,
                                    field_name.title(),
                                ),
                            )
                        )
                    )
                }
            )
        return graphene.Argument(
            type(
                "{}{}{}".format(
                    DYNAMIC_CLASS_NAME_PREFIX, self.prefix, field_name.title()
                ),
                (graphene.InputObjectType,),
                params,
            )
        )

    def get_field_options(self, field_name):
        """"""
        if field_name in self.connection_field.filter_fields:
            return self.connection_field.filter_fields[field_name]
        return {}

    @classmethod
    def get_range_params(cls, value):
        """Get params for `range` query.

        Syntax:

            /endpoint/?field_name__range={lower}__{upper}__{boost}
            /endpoint/?field_name__range={lower}__{upper}

        Example:

            http://localhost:8000/api/users/?age__range=16__67__2.0
            http://localhost:8000/api/users/?age__range=16__67
            http://localhost:8000/api/users/?age__range=16

        :param value:
        :type: str
        :return: Params to be used in `range` query.
        :rtype: dict
        """
        __values = cls.split_lookup_complex_value(value, maxsplit=3)
        __len_values = len(__values)

        if __len_values == 0:
            return {}

        params = {"gte": __values[0]}

        if __len_values == 3:
            params["lte"] = __values[1]
            params["boost"] = __values[2]
        elif __len_values == 2:
            params["lte"] = __values[1]

        return params

    @classmethod
    def get_gte_lte_params(cls, value, lookup):
        """Get params for `gte`, `gt`, `lte` and `lt` query.

        Syntax:

            /endpoint/?field_name__gt={lower}__{boost}
            /endpoint/?field_name__gt={lower}

        Example:

            http://localhost:8000/api/articles/?id__gt=1
            http://localhost:8000/api/articles/?id__gt=1__2.0

        :param value:
        :param lookup:
        :type value: str
        :type lookup: str
        :return: Params to be used in `range` query.
        :rtype: dict
        """
        __values = cls.split_lookup_complex_value(value, maxsplit=2)
        __len_values = len(__values)

        if __len_values == 0:
            return {}

        params = {lookup: __values[0]}

        if __len_values == 2:
            params["boost"] = __values[1]

        return params

    @classmethod
    def apply_filter_term(cls, queryset, options, value):
        """Apply `term` filter.

        Syntax:

            /endpoint/?field_name={value}

        Example:

            http://localhost:8000/api/articles/?tags=children

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

            /endpoint/?field_name__terms={value1}__{value2}
            /endpoint/?field_name__terms={value1}

        Note, that number of values is not limited.

        Example:

            http://localhost:8000/api/articles/?tags__terms=children__python
            http://localhost:8000/api/articles/?tags__terms=children

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

            /endpoint/?field_name__range={lower}__{upper}__{boost}
            /endpoint/?field_name__range={lower}__{upper}

        Example:

            http://localhost:8000/api/users/?age__range=16__67__2.0
            http://localhost:8000/api/users/?age__range=16__67
            http://localhost:8000/api/users/?age__range=16

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
            kwargs={options["field"]: cls.get_range_params(value)},
        )

    @classmethod
    def apply_query_exists(cls, queryset, options, value):
        """Apply `exists` filter.

        Syntax:

            /endpoint/?field_name__exists=true
            /endpoint/?field_name__exists=false

        Example:

            http://localhost:8000/api/articles/?tags__exists=true
            http://localhost:8000/api/articles/?tags__exists=false

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        _value_lower = value.lower()
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

            /endpoint/?field_name__prefix={value}

        Example:

            http://localhost:8000/api/articles/?tags__prefix=bio

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

            /endpoint/?field_name__wildcard={value}*
            /endpoint/?field_name__wildcard=*{value}
            /endpoint/?field_name__wildcard=*{value}*

        Example:

            http://localhost:8000/api/articles/?tags__wildcard=child*

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

            /endpoint/?field_name__contains={value}

        Example:

            http://localhost:8000/api/articles/?state__contains=lis

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

            /endpoint/?field_name__endswith={value}

        Example:

            http://localhost:8000/api/articles/?tags__endswith=dren

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

            /endpoint/?field_name__in={value1}__{value2}
            /endpoint/?field_name__in={value1}

        Note, that number of values is not limited.

        Example:

            http://localhost:8000/api/articles/?tags__in=children__python

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
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

            /endpoint/?field_name__gt={value}__{boost}
            /endpoint/?field_name__gt={value}

        Example:

            http://localhost:8000/api/articles/?id__gt=1__2.0
            http://localhost:8000/api/articles/?id__gt=1

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
            kwargs={options["field"]: cls.get_gte_lte_params(value, "gt")},
        )

    @classmethod
    def apply_query_gte(cls, queryset, options, value):
        """Apply `gte` functional query.

        Syntax:

            /endpoint/?field_name__gte={value}__{boost}
            /endpoint/?field_name__gte={value}

        Example:

            http://localhost:8000/api/articles/?id__gte=1__2.0
            http://localhost:8000/api/articles/?id__gte=1

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
            kwargs={options["field"]: cls.get_gte_lte_params(value, "gte")},
        )

    @classmethod
    def apply_query_lt(cls, queryset, options, value):
        """Apply `lt` functional query.

        Syntax:

            /endpoint/?field_name__lt={value}__{boost}
            /endpoint/?field_name__lt={value}

        Example:

            http://localhost:8000/api/articles/?id__lt=1__2.0
            http://localhost:8000/api/articles/?id__lt=1

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
            kwargs={options["field"]: cls.get_gte_lte_params(value, "lt")},
        )

    @classmethod
    def apply_query_lte(cls, queryset, options, value):
        """Apply `lte` functional query.

        Syntax:

            /endpoint/?field_name__lte={value}__{boost}
            /endpoint/?field_name__lte={value}

        Example:

            http://localhost:8000/api/articles/?id__lte=1__2.0
            http://localhost:8000/api/articles/?id__lte=1

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
            kwargs={options["field"]: cls.get_gte_lte_params(value, "lte")},
        )

    @classmethod
    def apply_query_isnull(cls, queryset, options, value):
        """Apply `isnull` functional query.

        Syntax:

            /endpoint/?field_name__isnull=true
            /endpoint/?field_name__isnull=false

        Example:

            http://localhost:8000/api/articles/?tags__isnull=true
            http://localhost:8000/api/articles/?tags__isnull=false

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        _value_lower = value.lower()
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

            /endpoint/?field_name__isnull={value1}__{value2}
            /endpoint/?field_name__exclude={valu1}

        Note, that number of values is not limited.

        Example:

            http://localhost:8000/api/articles/?tags__exclude=children__python
            http://localhost:8000/api/articles/?tags__exclude=children

        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        __values = cls.split_lookup_complex_value(value)

        __queries = []
        for __value in __values:
            __queries.append(~Q("term", **{options["field"]: __value}))

        if __queries:
            queryset = cls.apply_query(
                queryset=queryset,
                options=options,
                args=[six.moves.reduce(operator.or_, __queries)],
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

        :param view:
        :type view: rest_framework.viewsets.ReadOnlyModelViewSet
        :return: Filtering options.
        :rtype: dict

            filter_fields = {
                'id': '_id',
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
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        filter_fields = {}

        for arg, value in filter_args.items():
            field = self.connection_field.filter_args_mapping.get(arg, None)
            if field is None:
                continue
            filter_fields.update({field: {}})
            options = self.connection_field.filter_fields.get(field)
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

            if field in filter_fields and "lookups" not in filter_fields[field]:
                filter_fields[field].update(
                    {"lookups": tuple(ALL_LOOKUP_FILTERS_AND_QUERIES)}
                )
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
            field = self.connection_field.filter_args_mapping.get(arg, None)
            if field is None:
                continue
            if isinstance(value, dict):
                # For constructions like:
                # {filter:{title:{query:"Produce."}, category:{query:["Aaa"]}}}
                _query = value.pop("query")
                _field_options = copy.copy(value)
                value = _query
                # field_options.update(_field_options)
            query_params[field] = value
        return query_params

    def get_field_lookup_param(self, field_name):
        """Get field lookup param.

        :param field_name:
        :return:
        """
        field_options = dict(self.args).get(self.prefix, {}).get(field_name, {})
        return field_options.get("lookup", None)

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
        filter_fields = self.prepare_filter_fields()

        for field_name, values in query_params.items():
            query_param_list = self.split_lookup_filter(field_name, maxsplit=1)
            # field_name = query_param_list[0]

            if field_name in filter_fields:
                lookup_param = self.get_field_lookup_param(field_name)

                valid_lookups = filter_fields[field_name]["lookups"]

                # If we have default lookup given use it as a default and
                # do not require further suffix specification.
                default_lookup = None
                if "default_lookup" in filter_fields[field_name]:
                    default_lookup = filter_fields[field_name]["default_lookup"]

                if lookup_param is None or lookup_param in valid_lookups:

                    # If we have default lookup given use it as a default
                    # and do not require further suffix specification.
                    if lookup_param is None and default_lookup is not None:
                        lookup_param = str(default_lookup)

                    if isinstance(values, (list, tuple)):
                        values = [
                            __value.strip()
                            for __value in values
                            if __value.strip() != ""
                        ]
                    else:
                        values = [values]

                    if values:
                        filter_query_params[field_name] = {
                            "lookup": lookup_param,
                            "values": values,
                            "field": filter_fields[field_name].get(
                                "field", field_name
                            ),
                            "type": self.connection_field.document._doc_type.mapping.properties.name,
                        }
        return filter_query_params

    def filter(self, queryset):
        """"""
        filter_query_params = self.get_filter_query_params()

        for options in filter_query_params.values():
            # field_name = self.get_field_name(arg_name)
            # if field_name and self.field_belongs_to(field_name):
            #     options = self.get_field_options(field_name)
            #     if 'field' not in options:
            #         options.update({
            #             'field': arg_name,
            #         })
            #     if 'lookups' not in options:
            #         options.update({
            #             'lookups': STRING_LOOKUP_FILTERS,
            #         })
            #     if 'default_lookup' not in options:
            #         options.update({
            #             'default_lookup': LOOKUP_FILTER_TERM,
            #         })

            # For all other cases, when we don't have multiple values,
            # we follow the normal flow.
            for value in options["values"]:

                if options["lookup"] == LOOKUP_FILTER_TERMS:
                    queryset = self.apply_filter_terms(queryset, options, value)

                # `prefix` filter lookup
                elif options["lookup"] in (
                    LOOKUP_FILTER_PREFIX,
                    LOOKUP_QUERY_STARTSWITH,
                ):
                    queryset = self.apply_filter_prefix(
                        queryset, options, value
                    )

                # `range` filter lookup
                elif options["lookup"] == LOOKUP_FILTER_RANGE:
                    queryset = self.apply_filter_range(queryset, options, value)

                # `exists` filter lookup
                elif options["lookup"] == LOOKUP_FILTER_EXISTS:
                    queryset = self.apply_query_exists(queryset, options, value)

                # `wildcard` filter lookup
                elif options["lookup"] == LOOKUP_FILTER_WILDCARD:
                    queryset = self.apply_query_wildcard(
                        queryset, options, value
                    )

                # `contains` filter lookup
                elif options["lookup"] == LOOKUP_QUERY_CONTAINS:
                    queryset = self.apply_query_contains(
                        queryset, options, value
                    )

                # `in` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_IN:
                    queryset = self.apply_query_in(queryset, options, value)

                # `gt` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_GT:
                    queryset = self.apply_query_gt(queryset, options, value)

                # `gte` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_GTE:
                    queryset = self.apply_query_gte(queryset, options, value)

                # `lt` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_LT:
                    queryset = self.apply_query_lt(queryset, options, value)

                # `lte` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_LTE:
                    queryset = self.apply_query_lte(queryset, options, value)

                # `endswith` filter lookup
                elif options["lookup"] == LOOKUP_QUERY_ENDSWITH:
                    queryset = self.apply_query_endswith(
                        queryset, options, value
                    )

                # `isnull` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_ISNULL:
                    queryset = self.apply_query_isnull(queryset, options, value)

                # `exclude` functional query lookup
                elif options["lookup"] == LOOKUP_QUERY_EXCLUDE:
                    queryset = self.apply_query_exclude(
                        queryset, options, value
                    )

                # `term` filter lookup. This is default if no `default_lookup`
                # option has been given or explicit lookup provided.
                else:
                    queryset = self.apply_filter_term(queryset, options, value)

        return queryset
