import graphene
from graphene import Node
from graphene_elastic import (
    ElasticsearchObjectType,
    ElasticsearchConnectionField,
)
from graphene_elastic.filter_backends import (
    FilteringFilterBackend,
    PostFilterFilteringBackend,
    SearchFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
)
from graphene_elastic.constants import (
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_EXCLUDE,
    LOOKUP_QUERY_IN,
)

from search_index.documents import User as UserDocument


__all__ = (
    'User',
    'Query',
    'schema',
)


class User(ElasticsearchObjectType):

    class Meta:

        document = UserDocument
        interfaces = (Node,)
        filter_backends = [
            # FilteringFilterBackend,
            # PostFilterFilteringBackend,
            SearchFilterBackend,
            OrderingFilterBackend,
            DefaultOrderingFilterBackend,
        ]
        filter_fields = {
            'first_name': {
                'field': 'first_name.raw',
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
            'last_name': {
                'field': 'last_name.raw',
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
            'email': 'email.raw',
            'created_at': 'created_at',
            'is_active': 'is_active',
        }
        search_fields = {
            'first_name': None,
            'last_name': None,
            'email': None,
            'category': None,
        }
        ordering_fields = {
            'first_name': 'first_name.raw',
            'last_name': 'last_name.raw',
            'email': 'email.raw',
            'created_at': 'created_at',
            'is_active': 'is_active',
        }

        ordering_defaults = (
            'created_at',
        )
        post_filter_fields = {
            'pf_first_name': {
                'field': 'first_name.raw',
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
            'pf_last_name': {
                'field': 'last_name.raw',
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
            'pf_email': 'email.raw',
            'pf_created_at': 'created_at',
            'pf_is_active': 'is_active',
        }


class Query(graphene.ObjectType):
    """User query."""

    users = ElasticsearchConnectionField(
        User,
        enforce_first_or_last=True
    )


schema = graphene.Schema(
    query=Query
)
