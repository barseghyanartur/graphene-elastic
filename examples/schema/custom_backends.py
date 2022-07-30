from graphene_elastic.filter_backends.base import BaseBackend

from anysearch.search_dsl import A

__all__ = (
    'CustomFilterBackend',
)


class CustomFilterBackend(BaseBackend):
    """Custom filter backend."""

    prefix = 'post_filter'
    has_query_fields = False

    def filter(self, queryset):
        queryset = queryset.post_filter(
            'term', **{'category.raw': 'Python'}
        )
        aggregation = A('terms', field='category.raw')
        queryset.aggs.bucket('category_terms', aggregation)
        return queryset
