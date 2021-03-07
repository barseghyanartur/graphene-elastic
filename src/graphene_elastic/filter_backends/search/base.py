"""Base search backend."""

from ..base import BaseBackend
from ...exceptions import ImproperlyConfigured
from ...constants import MATCHING_OPTIONS, DEFAULT_MATCHING_OPTION

__title__ = 'graphene_elastic.filter_backends.search.common'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'BaseSearchFilterBackend',
)


class BaseSearchFilterBackend(BaseBackend):
    """Base search filter backend."""

    prefix = None
    query_backends = []
    matching = DEFAULT_MATCHING_OPTION

    def get_search_query_params(self):
        """Get search query params.

        This is equal to the `get_all_query_params` of the historical
        backend.

        :return: Dict with search query params.
        :rtype: dict
        """
        return dict(self.args).get(self.prefix, {})

    def get_query_backends(self):
        """Get query backends.

        :return:
        """
        raise NotImplementedError(
            "You should define `get_query_backends` method in your {} class"
            "".format(self.__class__.__name__)
        )

    def _get_query_backends(self):
        """Get query backends internal.

        :return:
        """
        try:
            return self.get_query_backends()
        except NotImplementedError as err:
            pass

        if not self.query_backends:
            raise NotImplementedError(
                "Your search backend shall either implement "
                "`get_query_backends` method or define `query_backends`"
                "property."
            )
        return self.query_backends[:]

    def filter(self, queryset):
        """Filter the queryset.

        :param queryset: Base queryset.
        :type queryset: elasticsearch_dsl.search.Search
        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        if self.matching not in MATCHING_OPTIONS:
            raise ImproperlyConfigured(
                "Your `matching` value does not match the allowed matching"
                "options: {}".format(', '.join(MATCHING_OPTIONS))
            )

        _query_backends = self._get_query_backends()

        if len(_query_backends) > 1:
            _queries = []
            for query_backend_cls in _query_backends:
                _query_backend = query_backend_cls(self)
                _queries.extend(
                    _query_backend.construct_search()
                )

            if _queries:
                queryset = queryset.query(
                    'bool',
                    **{self.matching: _queries}
                )

        elif len(_query_backends) == 1:
            _query_backend = _query_backends[0](self)
            _query = _query_backend.construct_search()
            queryset = queryset.query('bool', **{self.matching: _query})

        else:
            raise ImproperlyConfigured(
                "Search filter backend shall have at least one query_backend"
                "specified either in `query_backends` property or "
                "`get_query_backends` method. Make appropriate changes to"
                "your {} class".format(self.__class__.__name__)
            )

        return queryset
