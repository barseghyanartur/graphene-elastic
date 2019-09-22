"""
Some overrides of the original ``graphql_relay.connection.connectiontypes``
module. For sanity and ease of updates/sync with modifications from upstream,
this module isn't formatted in accordance with the rest of the package.
Pull requests code-style changes wouldn't be accepted.
"""

__title__ = 'graphene_elastic.relay.connectiontypes'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'Connection',
    'Facets',
)


class Connection(object):

    def __init__(self, edges, page_info, facets=None):
        self.edges = edges
        self.page_info = page_info
        self.facets = facets

    def to_dict(self):
        return {
            'edges': [e.to_dict() for e in self.edges],
            'pageInfo': self.page_info.to_dict(),
            'facets': {}
        }


class Facets(object):

    def __init__(self, facets):
        self.facets = facets

    def to_dict(self):
        return {
            'facets': self.facets,
        }


# class PageInfo(object):
#
#     def __init__(self, start_cursor="", end_cursor="",
#                  has_previous_page=False, has_next_page=False):
#         self.startCursor = start_cursor
#         self.endCursor = end_cursor
#         self.hasPreviousPage = has_previous_page
#         self.hasNextPage = has_next_page
#
#     def to_dict(self):
#         return {
#             'startCursor': self.startCursor,
#             'endCursor': self.endCursor,
#             'hasPreviousPage': self.hasPreviousPage,
#             'hasNextPage': self.hasNextPage,
#         }
#
#
# class Edge(object):
#
#     def __init__(self, node, cursor):
#         self.node = node
#         self.cursor = cursor
#
#     def to_dict(self):
#         return {
#             'node': self.node,
#             'cursor': self.cursor,
#         }
