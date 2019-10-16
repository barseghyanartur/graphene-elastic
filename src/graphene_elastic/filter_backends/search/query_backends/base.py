import six

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

    def prepare_search_fields(self):
        """Prepare search fields.

        Possible structures:

            search_fields = {
                'title': {'boost': 4, 'field': 'title.raw'},
                'content': {'boost': 2},
                'category': None,
            }

        We shall finally have:

            search_fields = {
                'title': {
                    'field': 'title.raw',
                    'boost': 4
                },
                'content': {
                    'field': 'content',
                    'boost': 2
                },
                'category': {
                    'field': 'category'
                }
            }

        Sample query would be:

            {
              allPostDocuments(search:{query:"Another"}) {
                pageInfo {
                  startCursor
                  endCursor
                  hasNextPage
                  hasPreviousPage
                }
                edges {
                  cursor
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }


        :return: Filtering options.
        :rtype: dict
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        filter_fields = {}

        # {'query': '', 'title': {'query': '', 'boost': 1}}

        for field, _ in self.search_args_mapping.items():
            filter_fields.update({field: {}})
            options = self.search_fields.get(field)
            # For constructions like 'category': 'category.raw' we shall
            # have the following:
            #
            if options is None or isinstance(options, six.string_types):
                filter_fields.update(
                    {
                        field: {"field": options or field}
                    }
                )
            elif "field" not in options:
                filter_fields.update({field: options})
                filter_fields[field]["field"] = field
            else:
                filter_fields.update({field: options})

        return filter_fields

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

    # def prepare_search_fields(self) -> dict:
    #     return self.search_backend.prepare_search_fields()
