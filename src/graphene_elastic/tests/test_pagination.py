import datetime
import time
import unittest
import dateutil
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

        self.num_future_users = 5
        self.future_users = factories.UserFactory.create_batch(
            self.num_future_users,
            created_at=self.faker.future_datetime()
        )
        for _post in self.future_users:
            _post.save()

        self.num_past_users = 59
        self.past_users = factories.UserFactory.create_batch(
            self.num_past_users,
            created_at=self.faker.past_datetime()
        )
        for _post in self.past_users:
            _post.save()

        self.num_all_users = self.num_past_users + self.num_future_users
        self.all_users = self.past_users + self.future_users

        time.sleep(3)

    def __test_pagination(self,
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

    def __test_pagination_required_first_or_last(self):
        """Test pagination.

        :param expected_num_results:
        :param first:
        :param last:
        :param after:
        :param before:
        :param ordering:
        :return:
        """
        _query = """
        {
          users(ordering:{createdAt:ASC}) {
            pageInfo {
              startCursor
              endCursor
              hasNextPage
              hasPreviousPage
            }
            edges {
              cursor
              node {
                email
                firstName
                lastName
                isActive
                createdAt
              }
            }
          }
        }
        """
        print(_query)
        executed = self.client.execute(_query)
        self.assertIn('errors', executed)
        self.assertIn('message', executed['errors'][0])
        self.assertIn('`first`', executed['errors'][0]['message'])
        self.assertIn('`last`', executed['errors'][0]['message'])

    def __test_pagination_required_correct_ordering_and_limits(
            self,
            expected_num_results,
            last=None
    ):
        """Test pagination.

        :param expected_num_results:
        :param last:
        :return:
        """
        _query = """
        {
          users(ordering:{createdAt:DESC}, last:%s) {
            pageInfo {
              startCursor
              endCursor
              hasNextPage
              hasPreviousPage
            }
            edges {
              cursor
              node {
                email
                firstName
                lastName
                isActive
                createdAt
              }
            }
          }
        }
        """ % last
        print(_query)

        executed = self.client.execute(_query)
        # fields_values_sorted = []
        self.assertEqual(
            len(executed['data']['users']['edges']),
            expected_num_results
        )
        _today = datetime.date.today()
        today = datetime.datetime(
            year=_today.year,
            month=_today.month,
            day=_today.day
        )
        for edge in executed['data']['users']['edges']:
            created_at = dateutil.parser.parse(edge['node']['createdAt'])
            self.assertGreater(created_at, today)

    def _test_pagination(self):
        """"Test pagination.

        :return:
        """
        with self.subTest('Test no params given, all items shall be present'):
            self.__test_pagination(
                self.num_all_posts
            )

        with self.subTest('Test first 12'):
            self.__test_pagination(
                first=12,
                expected_num_results=12
            )
        with self.subTest('Test no first or last params given when required'):
            self.__test_pagination_required_first_or_last()

        with self.subTest('Test correct ordering and limits'):
            self.__test_pagination_required_correct_ordering_and_limits(
                expected_num_results=self.num_future_users,
                last=self.num_future_users
            )

    def test_all(self):
        """Test all.

        Since we don't write in specific tests, it's more efficient to run
        them all from a single method in order to save on speed ups between
        tests.
        """
        self._test_pagination()


if __name__ == '__main__':
    unittest.main()
