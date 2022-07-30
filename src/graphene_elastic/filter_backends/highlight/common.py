from copy import deepcopy
import enum
import graphene
from graphene_elastic.types.json_string import ElasticJSONString
from stringcase import pascalcase as to_pascal_case

from ...constants import DYNAMIC_CLASS_NAME_PREFIX
from ..base import BaseBackend

__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019-2022 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'HighlightFilterBackend',
)


def highlight_resolver(parent, args, context=None, info=None):
    """Highlight resolver.

    :param parent:
    :param args:
    :param context:
    :param info:
    :return:
    """
    # return parent.meta.highlight
    return parent.meta._d_.get('highlight')


class HighlightField(ElasticJSONString):
    """Highlight field."""


class HighlightFilterBackend(BaseBackend):
    """Highlight filter backend."""

    prefix = 'highlight'
    has_query_fields = True

    @property
    def highlight_fields(self):
        """Highlight filter fields."""
        highlight_fields = getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('highlight_fields', {})
        return deepcopy(highlight_fields)

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        return field_name in self.highlight_fields

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

    def prepare_highlight_fields(self):
        """Prepare highlight fields.

        Possible structures:

            highlight_fields = {
                'title': {
                    'enabled': True,
                    'options': {
                        'pre_tags': ["<b>"],
                        'post_tags': ["</b>"],
                    }
                },
                'summary': {
                    'options': {
                        'fragment_size': 50,
                        'number_of_fragments': 3
                    }
                },
                'description': {},
            }

        Sample query would be:

            query {
              allPostDocuments(
                    search:{content:{value:"since"}, title:{value:"decide"}},
                    highlight:[category, content]
                ) {
                edges {
                  node {
                    title
                    content
                    highlight
                  }
                  cursor
                }
              }
            }

        :return: Filtering options.
        :rtype: dict
        """
        if not self.highlight_fields:
            return {}
        highlight_args = dict(self.args).get(self.prefix, [])

        highlight_fields = dict(self.highlight_fields)

        for field, options in self.highlight_fields.items():
            if 'enabled' in highlight_fields[field] \
                    or field not in highlight_args:
                highlight_fields[field]['enabled'] = True
            else:
                highlight_fields[field]['enabled'] = False

            if 'options' not in highlight_fields[field]:
                highlight_fields[field]['options'] = {}

        return highlight_fields

    def get_highlight_query_params(self):
        """Get highlight query params.

        :return: List of search query params.
        :rtype: list
        """
        highlight_args = dict(self.args).get(self.prefix, {})
        return highlight_args

    def filter(self, queryset):
        """Filter.

        :param queryset:
        :return:
        """
        highlight_query_params = self.get_highlight_query_params()
        highlight_fields = self.prepare_highlight_fields()

        for _field, _options in highlight_fields.items():
            if _field in highlight_query_params or _options['enabled']:
                queryset = queryset.highlight(_field, **_options['options'])

        return queryset

    def get_backend_document_fields(self):
        return {
            'highlight': graphene.Field(
                HighlightField,
                resolver=highlight_resolver
            ),
        }
