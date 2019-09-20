"""
Ordering backend.
"""
import graphene
from six import string_types

from ..base import BaseBackend
from ..queries import Direction
# from ...compat import nested_sort_entry

__title__ = 'graphene_elastic.filter_backends.ordering.common'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'DefaultOrderingFilterBackend',
    'OrderingFilterBackend',
)


class OrderingMixin(object):

    @property
    def _ordering_fields(self):
        """Ordering filter fields."""
        return getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('ordering_fields', {})

    @property
    def _ordering_args_mapping(self):
        return {k: k for k, v in self.ordering_fields.items()}

    @property
    def _ordering_defaults(self):
        """Ordering filter fields."""
        return getattr(
            self.connection_field.type._meta.node._meta,
            'filter_backend_options',
            {}
        ).get('ordering_defaults', {})

    def prepare_ordering_fields(self):
        """Prepare ordering fields.

        :return: Ordering options.
        :rtype: dict
        """
        ordering_args = dict(self.args).get(self.prefix)
        if not ordering_args:
            return {}

        ordering_fields = {}

        for arg, value in ordering_args.items():
            field = self.ordering_args_mapping.get(arg, None)
            if field is None:
                continue
            ordering_fields.update({field: {}})
            options = self.ordering_fields.get(field)

            if options is None or isinstance(options, string_types):
                ordering_fields[field] = {
                    'field': options or field
                }
            elif 'field' not in ordering_fields[field]:
                ordering_fields[field]['field'] = field
        return ordering_fields

    @classmethod
    def transform_ordering_params(cls, ordering_params, ordering_fields):
        """Transform ordering fields to elasticsearch-dsl Search.sort()
         dictionary parameters.

        :param ordering_params: List of fields to order by.
        :param ordering_fields: Prepared ordering fields
        :type: list of str
        :type: dict
        :return: Ordering parameters.
        :rtype: list
        """
        _ordering_params = []
        if isinstance(ordering_params, dict):
            for ordering_param, ordering_direction in ordering_params.items():
                field = ordering_fields[ordering_param]
                entry = {
                    field['field']: {
                        'order': ordering_direction,
                    }
                }

                # TODO: Once nested search is implemented, uncomment.
                # if 'path' in field:
                #     entry[field['field']].update(
                #         nested_sort_entry(field['path']))

                _ordering_params.append(entry)
        elif isinstance(ordering_params, (tuple, list)):
            for ordering_param in ordering_params:
                ordering_direction = Direction.ASC.value
                field = {'field': ordering_param}
                if ordering_param.startswith('-'):
                    field['field'] = ordering_param[1:]
                    ordering_direction = Direction.DESC.value
                entry = {
                    field['field']: {
                        'order': ordering_direction,
                    }
                }
                _ordering_params.append(entry)
        return _ordering_params


class OrderingFilterBackend(BaseBackend, OrderingMixin):
    """Ordering filter backend for Elasticsearch.

    Example:

        >>>   import graphene
        >>>   from graphene import Node
        >>>   from graphene_elastic import (
        >>>       ElasticsearchObjectType,
        >>>       ElasticsearchConnectionField,
        >>>   )
        >>>   from graphene_elastic.filter_backends import (
        >>>       FilteringFilterBackend,
        >>>       SearchFilterBackend,
        >>>       OrderingFilterBackend,
        >>>       DefaultOrderingFilterBackend,
        >>>   )
        >>>   from graphene_elastic.constants import (
        >>>       LOOKUP_FILTER_PREFIX,
        >>>       LOOKUP_FILTER_TERM,
        >>>       LOOKUP_FILTER_TERMS,
        >>>       LOOKUP_FILTER_WILDCARD,
        >>>       LOOKUP_QUERY_EXCLUDE,
        >>>       LOOKUP_QUERY_IN,
        >>>   )
        >>>
        >>>   from search_index.documents import Post as PostDocument
        >>>
        >>>   class Post(ElasticsearchObjectType):
        >>>
        >>>       class Meta(object):
        >>>           document = PostDocument
        >>>           interfaces = (Node,)
        >>>           filter_backends = [
        >>>               FilteringFilterBackend,
        >>>               SearchFilterBackend,
        >>>               OrderingFilterBackend,
        >>>               DefaultOrderingFilterBackend
        >>>           ]
        >>>           filter_fields = {
        >>>               'id': '_id',
        >>>               'title': {
        >>>                   'field': 'title.raw',
        >>>                   'lookups': [
        >>>                       LOOKUP_FILTER_TERM,
        >>>                       LOOKUP_FILTER_TERMS,
        >>>                       LOOKUP_FILTER_PREFIX,
        >>>                       LOOKUP_FILTER_WILDCARD,
        >>>                       LOOKUP_QUERY_IN,
        >>>                       LOOKUP_QUERY_EXCLUDE,
        >>>                   ],
        >>>                   'default_lookup': LOOKUP_FILTER_TERM,
        >>>               },
        >>>               'category': 'category.raw',
        >>>               'tags': 'tags.raw',
        >>>               'num_views': 'num_views',
        >>>           }
        >>>           search_fields = {
        >>>               'title': {'boost': 4},
        >>>               'content': {'boost': 2},
        >>>               'category': None,
        >>>           }
        >>>           ordering_fields = {
        >>>               'id': None,
        >>>               'title': 'title.raw',
        >>>               'created_at': 'created_at',
        >>>               'num_views': 'num_views',
        >>>           }
        >>>
        >>>           ordering_defaults = ('id', 'title',)

    The basic usage would be:

        query {
          allPostDocuments(ordering:{title:ASC}) {
            edges {
              node {
                title
                content
                category
                numViews
                createdAt
              }
            }
          }
        }
    """

    prefix = 'ordering'
    has_fields = True

    @property
    def ordering_fields(self):
        """Ordering filter fields."""
        return self._ordering_fields

    @property
    def ordering_args_mapping(self):
        return self._ordering_args_mapping

    def field_belongs_to(self, field_name):
        return field_name in self.ordering_fields

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:
        """
        return graphene.Argument(Direction)

    def get_ordering_query_params(self):
        """Get ordering query params.

        :return: Ordering params to be used for ordering.
        :rtype: list
        """
        # TODO: Support `mode` argument.
        query_params = dict(self.args).get(self.prefix)

        if not query_params:
            return []

        ordering_query_params = dict(query_params)
        # ordering_fields is always dict
        ordering_fields = self.prepare_ordering_fields()

        return self.transform_ordering_params(
            ordering_query_params,
            ordering_fields
        )

    def filter(self, queryset):
        """Filter the queryset.

        :param queryset: Base queryset.
        :type queryset: elasticsearch_dsl.search.Search
        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        ordering_query_params = self.get_ordering_query_params()
        if ordering_query_params:
            return queryset.sort(*ordering_query_params)

        return queryset


class DefaultOrderingFilterBackend(BaseBackend, OrderingMixin):
    """Default ordering filter backend for Elasticsearch.

    Make sure this is your last ordering backend.

    Example:

        >>>   import graphene
        >>>   from graphene import Node
        >>>   from graphene_elastic import (
        >>>       ElasticsearchObjectType,
        >>>       ElasticsearchConnectionField,
        >>>   )
        >>>   from graphene_elastic.filter_backends import (
        >>>       FilteringFilterBackend,
        >>>       SearchFilterBackend,
        >>>       OrderingFilterBackend,
        >>>       DefaultOrderingFilterBackend,
        >>>   )
        >>>   from graphene_elastic.constants import (
        >>>       LOOKUP_FILTER_PREFIX,
        >>>       LOOKUP_FILTER_TERM,
        >>>       LOOKUP_FILTER_TERMS,
        >>>       LOOKUP_FILTER_WILDCARD,
        >>>       LOOKUP_QUERY_EXCLUDE,
        >>>       LOOKUP_QUERY_IN,
        >>>   )
        >>>
        >>>   from search_index.documents import Post as PostDocument
        >>>
        >>>   class Post(ElasticsearchObjectType):
        >>>
        >>>       class Meta(object):
        >>>           document = PostDocument
        >>>           interfaces = (Node,)
        >>>           filter_backends = [
        >>>               FilteringFilterBackend,
        >>>               SearchFilterBackend,
        >>>               OrderingFilterBackend,
        >>>               DefaultOrderingFilterBackend
        >>>           ]
        >>>           filter_fields = {
        >>>               'id': '_id',
        >>>               'title': {
        >>>                   'field': 'title.raw',
        >>>                   'lookups': [
        >>>                       LOOKUP_FILTER_TERM,
        >>>                       LOOKUP_FILTER_TERMS,
        >>>                       LOOKUP_FILTER_PREFIX,
        >>>                       LOOKUP_FILTER_WILDCARD,
        >>>                       LOOKUP_QUERY_IN,
        >>>                       LOOKUP_QUERY_EXCLUDE,
        >>>                   ],
        >>>                   'default_lookup': LOOKUP_FILTER_TERM,
        >>>               },
        >>>               'category': 'category.raw',
        >>>               'tags': 'tags.raw',
        >>>               'num_views': 'num_views',
        >>>           }
        >>>           search_fields = {
        >>>               'title': {'boost': 4},
        >>>               'content': {'boost': 2},
        >>>               'category': None,
        >>>           }
        >>>           ordering_fields = {
        >>>               'id': None,
        >>>               'title': 'title.raw',
        >>>               'created_at': 'created_at',
        >>>               'num_views': 'num_views',
        >>>           }
        >>>
        >>>           ordering_defaults = ('id', 'title',)
    """

    prefix = 'ordering'
    has_fields = False

    @property
    def ordering_fields(self):
        """Ordering filter fields."""
        return self._ordering_fields

    @property
    def ordering_defaults(self):
        """Ordering filter fields."""
        return self._ordering_defaults

    def get_ordering_query_params(self):
        """Get ordering query params.

        :return: Ordering params to be used for ordering.
        :rtype: list
        """
        query_params = dict(self.args).get(self.prefix)
        ordering_query_params = dict(query_params) if query_params else {}
        ordering_params_present = False
        # Remove invalid ordering query params
        for query_param, ordering_direction in ordering_query_params.items():
            if query_param in self.ordering_fields:
                ordering_params_present = True
                break

        # If no valid ordering params specified, fall back to `view.ordering`
        if not ordering_params_present:
            return self.get_default_ordering_params()

        return {}

    def get_default_ordering_params(self):
        """Get the default ordering params for the view.

        :return: Ordering params to be used for ordering.
        :rtype: list
        """
        ordering = self.ordering_defaults

        if isinstance(ordering, string_types):
            ordering = [ordering]
        # For backwards compatibility require
        # default ordering to be keys in ordering_fields not field value
        # in order to be properly transformed
        if (
            ordering is not None
            and self.ordering_fields is not None
            and all(
                field.lstrip('-') in self.ordering_fields
                for field in ordering
            )
        ):
            return self.transform_ordering_params(
                ordering,
                self.prepare_ordering_fields()
            )
        return ordering

    def filter(self, queryset):
        """Filter the queryset.

        :param queryset: Base queryset.
        :type queryset: elasticsearch_dsl.search.Search
        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        ordering_query_params = self.get_ordering_query_params()

        if ordering_query_params:
            return queryset.sort(*ordering_query_params)

        return queryset
