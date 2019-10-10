__title__ = 'graphene_elastic.filter_backends.search.query_backends.base'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('BaseSearchQueryBackend',)


class BaseSearchQueryBackend(object):
    """Search query backend."""

    def __init__(self, search_backend):
        self.search_backend = search_backend

    @property
    def args(self) -> dict:
        return self.search_backend.args

    @property
    def prefix(self) -> str:
        return self.search_backend.prefix

    @property
    def search_args_mapping(self) -> dict:
        return self.search_backend.search_args_mapping

    @property
    def search_fields(self) -> dict:
        return self.search_backend.search_fields

    def construct_search(self):
        """Construct search.

        :return:
        """
        raise NotImplementedError(
            "You should implement `construct_search` method in your {} class"
            "".format(self.__class__.__name__)
        )

    def get_search_query_params(self) -> dict:
        return self.search_backend.get_search_query_params()

    def prepare_search_fields(self) -> dict:
        return self.search_backend.prepare_search_fields()
