from copy import deepcopy
import enum
import graphene
from graphene_elastic.types.json_string import ElasticJSONString
from stringcase import pascalcase as to_pascal_case

from ...constants import (
    DYNAMIC_CLASS_NAME_PREFIX,
    ALL_SUGGESTERS,
    SUGGESTER_COMPLETION,
    SUGGESTER_TERM,
    SUGGESTER_PHRASE,
)
from ..base import BaseBackend

__title__ = 'graphene_elastic.filter_backends.suggest.common'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019-2020 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'SuggestFilterBackend',
)


def suggest_resolver(parent, args, context=None, info=None):
    """Suggest resolver.

    :param parent:
    :param args:
    :param context:
    :param info:
    :return:
    """
    # return parent.meta.highlight
    return parent.meta._d_.get('suggest')


class SuggestField(ElasticJSONString):
    """Suggest field."""


class SuggestFilterBackend(BaseBackend):
    """Suggest filter backend."""

    prefix = 'suggest'
    has_query_fields = True

    @property
    def suggest_fields(self):
        """Suggest filter fields."""
        suggest_fields = getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('suggest_fields', {})
        return deepcopy(suggest_fields)

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        return field_name in self.suggest_fields

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

        if not params:
            return None
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

    def prepare_suggest_fields(self):
        """Prepare suggest fields.

        Possible structures:

            suggest_fields = {
                'title_suggest': {
                    'field': 'title.suggest',
                    'default_suggester': SUGGESTER_COMPLETION,
                    'options': {
                        'size': 20,
                        'skip_duplicates': True,
                    }
                },
                'title_suggest_context': {
                    'field': 'title.suggest_context',
                    'suggesters': [SUGGESTER_COMPLETION,],
                    'default_suggester': SUGGESTER_COMPLETION,
                    'completion_options': {
                        'category_filters': {
                            'title_tag': 'tag',
                            'title_state': 'state',
                            'title_publisher': 'publisher',
                        },
                    },
                    'options': {
                        'size': 20,
                    },
                },
                'publisher_suggest': 'publisher.suggest',
                'tag_suggest': 'tags.suggest',
            }

        Sample query would be:

            query {
              allPostDocuments(
                    search:{content:{value:"since"}, title:{value:"decide"}},
                    suggest:[category, content]
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
        # if not self.suggest_fields:
        #     return {}

        suggest_args = dict(self.args).get(self.prefix, [])
        import ipdb; ipdb.set_trace()
        if not suggest_args:
            return {}

        # suggest_fields = dict(self.suggest_fields)
        #
        # for field, options in suggest_fields.items():
        #     if not isinstance(options, dict):
        #         options = {
        #             'field': options,
        #         }
        #
        #     if 'suggesters' not in options:
        #         options['suggesters'] = tuple(
        #             ALL_SUGGESTERS
        #         )
        #
        #     if 'options' not in options:
        #         options['options'] = {}
        #
        #     suggest_fields[field] = options

        return suggest_fields

    def get_suggest_query_params(self) -> dict:
        """Get suggest query params.

        :return: List of search query params.
        :rtype: list
        """
        suggest_args = dict(self.args).get(self.prefix, {})
        return suggest_args

    @classmethod
    def apply_suggester_term(cls, suggester_name, queryset, options, value):
        """Apply `term` suggester.
        :param suggester_name:
        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type suggester_name: str
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return queryset.suggest(
            suggester_name,
            value,
            term={'field': options['field']}
        )

    @classmethod
    def apply_suggester_phrase(cls, suggester_name, queryset, options, value):
        """Apply `phrase` suggester.
        :param suggester_name:
        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type suggester_name: str
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        return queryset.suggest(
            suggester_name,
            value,
            phrase={'field': options['field']}
        )

    @classmethod
    def apply_suggester_completion(cls,
                                   suggester_name,
                                   queryset,
                                   options,
                                   value):
        """Apply `completion` suggester.
        :param suggester_name:
        :param queryset: Original queryset.
        :param options: Filter options.
        :param value: value to filter on.
        :type suggester_name: str
        :type queryset: elasticsearch_dsl.search.Search
        :type options: dict
        :type value: str
        :return: Modified queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        completion_kwargs = {
            'field': options['field'],
        }
        if 'size' in options:
            completion_kwargs['size'] = options['size']
        if 'contexts' in options:
            completion_kwargs['contexts'] = options['contexts']
        if 'skip_duplicates' in options:
            completion_kwargs['skip_duplicates'] = options['skip_duplicates']
        return queryset.suggest(
            suggester_name,
            value,
            completion=completion_kwargs
        )

    def filter(self, queryset):
        """Filter.

        :param queryset:
        :return:
        """
        suggest_query_params = self.get_suggest_query_params()
        suggest_fields = self.prepare_suggest_fields()
        if not suggest_query_params:
            import ipdb; ipdb.set_trace()
            return queryset
        # for _field, _options in suggest_fields.items():
        #     if _field in suggest_query_params or _options['enabled']:
        #         queryset = queryset.suggest(_field, **_options['options'])

        for suggester_name, options in suggest_query_params.items():
            # We don't have multiple values here.
            for value in options['values']:
                # `term` suggester
                if options['suggester'] == SUGGESTER_TERM:
                    queryset = self.apply_suggester_term(suggester_name,
                                                         queryset,
                                                         options,
                                                         value)

                # `phrase` suggester
                elif options['suggester'] == SUGGESTER_PHRASE:
                    queryset = self.apply_suggester_phrase(suggester_name,
                                                           queryset,
                                                           options,
                                                           value)

                # `completion` suggester
                elif options['suggester'] == SUGGESTER_COMPLETION:
                    queryset = self.apply_suggester_completion(suggester_name,
                                                               queryset,
                                                               options,
                                                               value)

        return queryset

    def get_backend_document_fields(self):
        return {
            'suggest': graphene.Field(
                SuggestField,
                resolver=suggest_resolver
            ),
        }
