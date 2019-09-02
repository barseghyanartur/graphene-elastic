import time
import unittest
import factories
from .base import BaseGrapheneElasticTestCase

__all__ = (
    'PaginationTestCase',
)


class PaginationTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(PaginationTestCase, self).setUp()

        # Important thing to know about the factories.
        # The `PostFactory` factory has `num_views` between 0 and 1_000.
        # The `ManyViewsPostFactory` factory has `num_views` between
        # 2_000 and 10_000.
        self.num_elastic_posts = 22
        self.elastic_posts = factories.PostFactory.create_batch(
            self.num_elastic_posts,
            category='Elastic',
            tags=None
        )
        for _post in self.elastic_posts:
            _post.save()

        self.num_django_posts = 11
        self.django_posts = factories.PostFactory.create_batch(
            self.num_django_posts,
            category='Django'
        )
        for _post in self.django_posts:
            _post.save()

        self.num_all_posts = self.num_elastic_posts + self.num_django_posts
        self.all_posts = (
            self.elastic_posts + self.django_posts
        )

        time.sleep(3)

    def _test_pagination(self,
                         expected_num_results,
                         first=None,
                         last=None,
                         after=None,
                         before=None):
        """Test pagination.

        :param expected_num_results:
        :param first:
        :param last:
        :param after:
        :param before:
        :return:
        """
        _query_args_list = []
        _query_args = ""
        if first:
            _query_args_list.append('first:{}'.format(first))
        if last:
            _query_args_list.append('last:{}'.format(last))
        if after:
            _query_args_list.append('after:"{}"'.format(after))
        if before:
            _query_args_list.append('before:"{}"'.format(before))

        if _query_args_list:
            _query_args = '({})'.format(''.join(_query_args_list))

        _query = """
        {
          allPostDocuments%s {
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
        """ % _query_args
        print(_query)
        executed = self.client.execute(_query)
        fields_values_sorted = []
        # TODO: Perhaps, check firsts and lasts?
        self.assertEqual(
            len(executed['data']['allPostDocuments']['edges']),
            expected_num_results
        )

    def test_pagination(self):
        """"Test pagination.

        :return:
        """
        with self.subTest('Test no params given, all items shall be present'):
            self._test_pagination(
                self.num_all_posts
            )

        with self.subTest('Test no params given, all items shall be present'):
            self._test_pagination(
                first=12,
                expected_num_results=12
            )


if __name__ == '__main__':
    unittest.main()
