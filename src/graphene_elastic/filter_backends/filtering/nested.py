from collections import OrderedDict, ChainMap
from copy import deepcopy

from stringcase import pascalcase as to_pascal_case

import graphene

from graphene_elastic.types.json_string import ElasticJSONString

from ...constants import (
    ALL_LOOKUP_FILTERS_AND_QUERIES,
    DYNAMIC_CLASS_NAME_PREFIX,
    VALUE,
)
from .common import FilteringFilterBackend
from .queries import LOOKUP_FILTER_MAPPING

__all__ = ("NestedFilteringFilterBackend",)


def is_nested_field(field):
    return field.type == ElasticJSONString


class NestedFilteringFilterBackend(FilteringFilterBackend):
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
            print(is_filterable_func(field), is_nested_field(value))
            if is_filterable_func(field) and is_nested_field(value):
                if self.field_belongs_to(field):
                    for (
                        sub_field_name,
                        sub_field_value,
                    ) in self.get_field_options(field).items():
                        params.setdefault(field, {}).update(
                            {
                                sub_field_name: self.get_field_type(
                                    field_name=sub_field_name,
                                    field_value=sub_field_value,
                                    base_field_type=get_type_func(
                                        sub_field_value
                                    ),
                                )
                            }
                        )
        print(params)
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

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
        if not self.nested_fields:
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
                    to_pascal_case(field_name),
                ),
                (graphene.InputObjectType,),
                params,
            )
        )

    def filter(self, queryset):
        ...