from copy import deepcopy
import graphene
from stringcase import pascalcase as to_pascal_case

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
from .mixins import FilteringFilterMixin
from .queries import LOOKUP_FILTER_MAPPING

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019-2022 Artur Barseghyan"
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

        return deepcopy(filter_fields)

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
        if isinstance(field_options, dict) and "type" in field_options:
            if field_options["type"] in ("nested", "object"):
                return self.get_nested_field_type(
                    field_name,
                    field_value,
                    base_field_type,
                    field_options
                )

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

    def get_nested_field_type(
        self,
        field_name,
        field_value,
        base_field_type,
        field_options
    ):
        params = {}
        for sub_field_name in field_options.get("properties", []):
            _field_name = "{}.{}".format(field_name, sub_field_name)
            _field_type = self.get_field_type(
                _field_name, field_value, base_field_type)
            _field_type.__name__ = "{}{}{}{}".format(
                DYNAMIC_CLASS_NAME_PREFIX,
                to_pascal_case(self.prefix),
                self.connection_field.type.__name__,
                to_pascal_case(_field_name.replace(".", "_"))
            )
            params.update({sub_field_name: _field_type})

        return graphene.Argument(
            type(
                "{}{}{}{}".format(
                    DYNAMIC_CLASS_NAME_PREFIX,
                    to_pascal_case(self.prefix),
                    self.connection_field.type.__name__,
                    to_pascal_case(field_name.replace(".", "_"))
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
        """Prepare filter fields

        Assume that we have a document like this.

        ```python
        class Comment(InnerDoc):
            author = Text(fields={'raw': Keyword()})
            content = Text(analyzer='snowball')
            created_at = Date()

            def age(self):
                return datetime.now() - self.created_at

        class Post(Document):
            title = Text()
            title_suggest = Completion()
            created_at = Date()
            published = Boolean()
            category = Text(
                analyzer=html_strip,
                fields={'raw': Keyword()}
            )

            comments = Nested(Comment)
        ```

        Possible structures:

            filter_fields = {
                'title': {
                    'type': 'normal|object|nested',
                    'field': 'title'    # custom field name
                    'lookups': [
                        ... # custom lookup list
                    ],
                    'default_lookup': ... # custom default lookup
                },
                'created_at': {
                    'type': 'normal',
                    'field': 'created_at',
                    'lookups': [
                        LOOKUP_FILTER_RANGE # only range
                    ]
                },
                'published': LOOKUP_FILTER_TERM  # treated as default lookup
                ...
            }

        We shall finally have:

            filter_fields = {
                'title': {
                    'type': 'normal',
                    'field': 'title.raw',
                    'lookups': [
                        ...
                    ],
                    'default_lookup': ...
                },
                ... # any else fields indexed of this document
                'comments': {
                    'type': 'nested',
                    'properties': {
                        'author': {
                            'type': 'normal',
                            'field': 'comments.author',
                            ...
                        },
                        'content': {
                            'type': 'normal',
                            'field': 'comments.content',
                            ...
                        }
                    }
                }
            }
        """
        def _recursive_correct_filter_fields(
            filter_fields,
            root_field=None,
            is_nested=False
        ):
            # TODO: Generate complete filter_fields
            data = {}
            for field_name, field_options in filter_fields.items():
                data[field_name] = {}
                default_lookup, lookups = None, None
                if isinstance(field_options, str):
                    field = field_options
                    field_type = "normal"
                elif isinstance(field_options, dict):
                    field = field_options.get("field", field_name)
                    default_lookup = field_options.get("default_lookup")
                    lookups = field_options.get("lookups")
                    field_type = field_options.get("type", "normal")
                else:
                    raise TypeError(
                        "Field option must be type of str or dict.")

                if lookups is None:
                    lookups = ALL_LOOKUP_FILTERS_AND_QUERIES

                if default_lookup is None:
                    default_lookup = lookups[0]

                field = "{}.{}".format(
                    root_field, field) if root_field else field
                data[field_name]["field"] = field
                data[field_name]["type"] = field_type

                if field_type == "normal":
                    data[field_name]["lookups"] = lookups
                    data[field_name]["default_lookup"] = default_lookup
                else:
                    data[field_name]["properties"] = \
                        _recursive_correct_filter_fields(
                            field_options["properties"],
                            root_field=field,
                            is_nested=field_type == "nested"
                        )
                if is_nested:
                    data[field_name]["path"] = root_field
            return data

        return _recursive_correct_filter_fields(self.filter_fields)

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

    def get_field_options(self, field_name, filter_fields=None):
        """默认从Node中配置中读取，如果没有则从document中读取

        可能的字段名:
        1. author
        2. comments.author
        3. comments.author.name
        """
        if filter_fields is None:
            filter_fields = self.filter_fields

        search_path = field_name.split(".")
        data = deepcopy(filter_fields)
        for p in search_path:
            if "properties" in data:
                data = data["properties"]
            data = data.get(p, {})
        return data or None

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
                },
                'comments': {
                    'author': {
                        'name': {
                            'value': 'Elastic'
                        }
                    }
                }
            }

            filter_fields = {
                'category': {
                    'field': 'category.raw',
                    'type': 'normal',
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
                },
                'comments': {
                    'field': 'comments',
                    'type': 'nested',
                    'properties': {
                        'author': {
                            'type': 'object',
                            'path': 'comments.author',
                            'properties': {
                                'name': {
                                    'type': 'normal',
                                    'field': 'author.name',
                                    'default_lookups': 'term',
                                    'lookups': (
                                        ...
                                    )
                                }
                            }
                        }
                    }
                }
            }

            field_name = 'category'
            {
                'inventory_type': {'value': '1'},
                'spu': {
                    'supplier_entityms_entity_id': {
                        'contains': 'Elastic'
                    },
                    'brand': {
                        'code': {
                            'term': 'Elastic'
                        }
                    }
                }
            }
        """

        query_params = self.prepare_query_params()     # Shall be fixed
        filter_query_params = []
        filter_fields = self.prepare_filter_fields()   # Correct

        def _recursive_get_lookup_param_options(
            query_dict: dict,
            predefined_filter_fields: dict,
            ret=None
        ):
            """In-depth traversal of the tree dict to generate a query list."""
            filter_fields = deepcopy(predefined_filter_fields)
            for field_name, lookup_params in query_dict.items():
                if field_name not in filter_fields:
                    continue

                field_options = filter_fields[field_name]
                field_type = field_options["type"]

                if field_type in ("nested", "object"):
                    _recursive_get_lookup_param_options(
                        query_dict=lookup_params,
                        predefined_filter_fields=filter_fields[
                            field_name
                        ]["properties"],
                        ret=ret
                    )
                else:
                    valid_lookup = field_options.get("lookups", ())
                    default_lookup = field_options.get("default_lookup", None)

                    for lookup_param, lookup_options in lookup_params.items():
                        lookup = None
                        if lookup_param is VALUE:
                            lookup = default_lookup
                        elif lookup_param in valid_lookup:
                            lookup = lookup_param

                        if lookup_options is not None:
                            ret.append({
                                "lookup": lookup,
                                "values": lookup_options,
                                "path": field_options.get("path"),
                                "field": field_options.get(
                                    "field",
                                    field_name
                                ),
                                "type": self.doc_type.mapping.properties.name,
                            })

        _recursive_get_lookup_param_options(
            query_dict=query_params,
            predefined_filter_fields=filter_fields,
            ret=filter_query_params
        )
        return filter_query_params

    def filter(self, queryset):
        """Filter."""
        filter_query_params = self.get_filter_query_params()

        for filter_query in filter_query_params:

            # For all other cases, when we don't have multiple values,
            # we follow the normal flow.
            if filter_query["lookup"] == LOOKUP_FILTER_TERMS:
                queryset = self.apply_filter_terms(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `prefix` filter lookup
            elif filter_query["lookup"] in (
                LOOKUP_FILTER_PREFIX,
                LOOKUP_QUERY_STARTSWITH,
            ):
                queryset = self.apply_filter_prefix(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `range` filter lookup
            elif filter_query["lookup"] == LOOKUP_FILTER_RANGE:
                queryset = self.apply_filter_range(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `exists` filter lookup
            elif filter_query["lookup"] == LOOKUP_FILTER_EXISTS:
                queryset = self.apply_query_exists(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `wildcard` filter lookup
            elif filter_query["lookup"] == LOOKUP_FILTER_WILDCARD:
                queryset = self.apply_query_wildcard(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `contains` filter lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_CONTAINS:
                queryset = self.apply_query_contains(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `in` functional query lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_IN:
                queryset = self.apply_query_in(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `gt` functional query lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_GT:
                queryset = self.apply_query_gt(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `gte` functional query lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_GTE:
                queryset = self.apply_query_gte(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `lt` functional query lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_LT:
                queryset = self.apply_query_lt(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `lte` functional query lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_LTE:
                queryset = self.apply_query_lte(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `endswith` filter lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_ENDSWITH:
                queryset = self.apply_query_endswith(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `isnull` functional query lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_ISNULL:
                queryset = self.apply_query_isnull(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `exclude` functional query lookup
            elif filter_query["lookup"] == LOOKUP_QUERY_EXCLUDE:
                queryset = self.apply_query_exclude(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

            # `term` filter lookup. This is default if no `default_lookup`
            # filter_query has been given or explicit lookup provided.
            else:
                queryset = super(
                    FilteringFilterBackend,
                    self
                ).apply_filter_term(
                    queryset,
                    filter_query,
                    filter_query['values']
                )

        return queryset
