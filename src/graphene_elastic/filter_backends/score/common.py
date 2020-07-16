import graphene
from graphene import Float

from ..base import BaseBackend

__title__ = 'graphene_elastic.filter_backends.score.common'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019-2020 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'ScoreFilterBackend',
)


def score_resolver(parent, args, context=None, info=None):
    """Score resolver.

    :param parent:
    :param args:
    :param context:
    :param info:
    :return:
    """
    return parent.meta._d_.get('score')


class ScoreField(Float):
    """Score field."""


class ScoreFilterBackend(BaseBackend):
    """Score filter backend.

        Sample query would be:

            query {
              allPostDocuments(
                    search:{content:{value:"since"}, title:{value:"decide"}}
                ) {
                edges {
                  node {
                    title
                    content
                    score
                  }
                  cursor
                }
              }
            }
    """

    prefix = 'score'
    has_query_fields = False
    score_field_name = 'score'

    @property
    def score_fields(self):
        """Score filter fields."""
        return {self.score_field_name: '_score'}

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        return field_name in self.score_fields

    def filter(self, queryset):
        """Filter.

        :param queryset:
        :return:
        """
        return queryset

    def get_backend_document_fields(self):
        return {
            self.score_field_name: graphene.Field(
                ScoreField,
                resolver=score_resolver
            ),
        }
