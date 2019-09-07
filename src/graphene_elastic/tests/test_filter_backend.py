import time
import unittest
from graphene.utils.str_converters import to_camel_case
import factories
from ..constants import (
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_EXISTS,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_WILDCARD,
    # LOOKUP_FILTER_REGEXP,
    # LOOKUP_FILTER_FUZZY,
    # LOOKUP_FILTER_TYPE,
    LOOKUP_FILTER_GEO_DISTANCE,
    LOOKUP_FILTER_GEO_POLYGON,
    LOOKUP_FILTER_GEO_BOUNDING_BOX,
    LOOKUP_QUERY_CONTAINS,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_STARTSWITH,
    LOOKUP_QUERY_ENDSWITH,
    LOOKUP_QUERY_ISNULL,
    LOOKUP_QUERY_EXCLUDE,
    VALUE,
    LOWER,
    UPPER,
)
from .base import BaseGrapheneElasticTestCase

__all__ = (
    'FilterBackendElasticTestCase',
)


class FilterBackendElasticTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(FilterBackendElasticTestCase, self).setUp()

        # Important thing to know about the factories.
        # The `PostFactory` factory has `num_views` between 0 and 1_000.
        # The `ManyViewsPostFactory` factory has `num_views` between
        # 2_000 and 10_000.
        self.num_elastic_posts = 4
        self.elastic_posts = factories.PostFactory.create_batch(
            self.num_elastic_posts,
            category='Elastic',
            tags=None
        )
        for _post in self.elastic_posts:
            _post.save()

        self.num_django_posts = 3
        self.django_posts = factories.PostFactory.create_batch(
            self.num_django_posts,
            category='Django'
        )
        for _post in self.django_posts:
            _post.save()

        self.num_python_posts = 2
        self.python_posts = factories.ManyViewsPostFactory.create_batch(
            self.num_python_posts,
            category='Python',
        )
        for _post in self.python_posts:
            _post.save()

        self.num_all_posts = (
            self.num_elastic_posts +
            self.num_django_posts +
            self.num_python_posts
        )
        self.all_posts = (
            self.elastic_posts + self.django_posts + self.python_posts
        )

        time.sleep(3)

    def __test_filter_text_lookups(self,
                                   query,
                                   num_posts,
                                   lookup=VALUE,
                                   field='category'):
        """Test filter text lookups (on field `category`).

        :param query:
        :param num_posts:
        :param field:
        :return:
        """
        _query = """
        query {
          allPostDocuments(filter:{%s:{%s:%s}}) {
            edges {
              node {
                category
                title
                content
                numViews
                comments
              }
            }
          }
        }
        """ % (field, lookup, query)
        print(_query)
        executed = self.client.execute(_query)
        self.assertEqual(
            len(executed['data']['allPostDocuments']['edges']),
            num_posts
        )

    def __test_filter_number_lookups(self,
                                     value,
                                     num_posts,
                                     lookup=LOOKUP_QUERY_GT):
        """Test filter number lookups (on field `num_views`).

        :param value:
        :param num_posts:
        :param lookup:
        :return:
        """
        _query = """
        query {
          allPostDocuments(filter:{numViews:{%s:%s}}) {
            edges {
              node {
                category
                title
                content
                numViews
                comments
              }
            }
          }
        }
        """ % (lookup, value)
        executed = self.client.execute(_query)
        self.assertEqual(
            len(executed['data']['allPostDocuments']['edges']),
            num_posts
        )

    def _test_filter_term_terms_lookup(self):
        """"Test filter `term` and `terms` lookups (on field `category`).

        :return:
        """
        with self.subTest('Test filter on field `category` "Django" '
                          'using default lookup (`term`)'):
            self.__test_filter_text_lookups(
                '"Django"',
                self.num_django_posts
            )

        with self.subTest('Test filter on field `category` "Django" '
                          'using `term` lookup'):
            self.__test_filter_text_lookups(
                '"Django"',
                self.num_django_posts,
                lookup=LOOKUP_FILTER_TERM
            )

        with self.subTest('Test filter on field `category` "Elastic" '
                          'using default lookup (`term`)'):
            self.__test_filter_text_lookups(
                '"Elastic"',
                self.num_elastic_posts
            )

        with self.subTest('Test filter on field `category` "Elastic" '
                          'using `term` lookup'):
            self.__test_filter_text_lookups(
                '"Elastic"',
                self.num_elastic_posts,
                LOOKUP_FILTER_TERM
            )

        with self.subTest('Test filter on field `category` '
                          '["Elastic", "Django"] using `terms` lookup'):
            self.__test_filter_text_lookups(
                '["Elastic", "Django"]',
                self.num_elastic_posts + self.num_django_posts,
                LOOKUP_FILTER_TERMS
            )

        with self.subTest('Test filter on field `category` '
                          '["Elastic", "Django"] using `in` lookup'):
            self.__test_filter_text_lookups(
                '["Elastic", "Django"]',
                self.num_elastic_posts + self.num_django_posts,
                LOOKUP_QUERY_IN
            )

    def _test_filter_prefix_starts_ends_with_contains_wildcard_lookups(self):
        """"Test filters `prefix`, `starts_with` and `ends_with` lookups (on
        field `category`).

        :return:
        """
        with self.subTest('Test filter on field `category` "Elastic" '
                          'using `contains` lookup'):
            self.__test_filter_text_lookups(
                '"ytho"',
                self.num_python_posts,
                LOOKUP_QUERY_CONTAINS
            )

        with self.subTest('Test filter on field `category` "Elastic" '
                          'using `wildcard` lookup'):
            self.__test_filter_text_lookups(
                '"*ytho*"',
                self.num_python_posts,
                LOOKUP_FILTER_WILDCARD
            )

        with self.subTest('Test filter on field `category` "Elastic" '
                          'using `prefix` lookup'):
            self.__test_filter_text_lookups(
                '"Pyth"',
                self.num_python_posts,
                to_camel_case(LOOKUP_FILTER_PREFIX)
            )

        with self.subTest('Test filter on field `category` "Elastic" '
                          'using `starts_with` lookup'):
            self.__test_filter_text_lookups(
                '"Pyth"',
                self.num_python_posts,
                to_camel_case(LOOKUP_QUERY_STARTSWITH)
            )

        with self.subTest('Test filter on field `category` "Elastic" '
                          'using `ends_with` lookup'):
            self.__test_filter_text_lookups(
                '"ython"',
                self.num_python_posts,
                to_camel_case(LOOKUP_QUERY_ENDSWITH)
            )

    def _test_filter_exclude_lookup(self):
        """"Test filter `exclude` lookup (on field `category`).

        :return:
        """
        with self.subTest('Test filter on field `category` "Elastic" '
                          'using `exclude` lookup'):
            self.__test_filter_text_lookups(
                '"Python"',
                self.num_all_posts - self.num_python_posts,
                LOOKUP_QUERY_EXCLUDE
            )

    def _test_filter_exists_is_null_lookups(self):
        """"Test filter `exists` lookup (on fields `category`
        and `i_do_not_exist`).

        :return:
        """
        with self.subTest('Test filter on field `category`'
                          'using `exists` lookup'):
            self.__test_filter_text_lookups(
                'true',
                self.num_all_posts,
                LOOKUP_FILTER_EXISTS
            )

        with self.subTest('Test filter on field `category`'
                          'using `is_null` lookup'):
            self.__test_filter_text_lookups(
                'false',
                self.num_all_posts,
                to_camel_case(LOOKUP_QUERY_ISNULL)
            )

        # TODO: See if we can test this case
        # with self.subTest('Test filter on field `i_do_not_exist`'
        #                   'using `exists` lookup'):
        #     self._test_filter_text_lookups(
        #         'true',
        #         0,
        #         LOOKUP_FILTER_EXISTS,
        #         field='i_do_not_exist'
        #     )

    def _test_filter_gt_gte_lt_lte_range_lookups(self):
        """"Test filter `gt`, `gte`, `lt`, `lte`, `range` lookups (on
        field `num_views`).

        :return:
        """
        # This should be all posts, since minimum value for posts is 0.
        with self.subTest('Test filter on field `num_views` '
                          'using `gt` lookup'):
            self.__test_filter_number_lookups(
                '"0.1"',
                self.num_all_posts
            )

        # This should be Python posts only, since they may start at 2_000.
        with self.subTest('Test filter on field `num_views` '
                          'using `gt` lookup'):
            self.__test_filter_number_lookups(
                '"1999"',
                self.num_python_posts
            )

        # This shall be all posts (including 0).
        with self.subTest('Test filter on field `num_views` '
                          'using `gte` lookup'):
            self.__test_filter_number_lookups(
                '"0"',
                self.num_all_posts,
                lookup=LOOKUP_QUERY_GTE
            )

        # This shall be Python posts only, since they may start at 2_000.
        with self.subTest('Test filter on field `num_views` '
                          'using `gte` lookup'):
            self.__test_filter_number_lookups(
                '"2000"',
                self.num_python_posts,
                lookup=LOOKUP_QUERY_GTE
            )

        # This shall be all posts, since maximum is 10_000.
        with self.subTest('Test filter on field `num_views` '
                          'using `lt` lookup'):
            self.__test_filter_number_lookups(
                '"10001"',
                self.num_all_posts,
                lookup=LOOKUP_QUERY_LT
            )

        # This shall exclude Python posts, since they start at 2_000.
        with self.subTest('Test filter on field `num_views` '
                          'using `lt` lookup'):
            self.__test_filter_number_lookups(
                '"2000"',
                self.num_all_posts - self.num_python_posts,
                lookup=LOOKUP_QUERY_LT
            )

        # This shall be all posts, since maximum is 10_000.
        with self.subTest('Test filter on field `num_views` '
                          'using `lte` lookup'):
            self.__test_filter_number_lookups(
                '"10000"',
                self.num_all_posts,
                lookup=LOOKUP_QUERY_LTE
            )

        # This shall exclude all Python posts, since they start at 2_000
        with self.subTest('Test filter on field `num_views` '
                          'using `lte` lookup'):
            self.__test_filter_number_lookups(
                '"1999"',
                self.num_all_posts - self.num_python_posts,
                lookup=LOOKUP_QUERY_LTE
            )

        # To test range successfully, since we do not make specific range
        # factories in between, we simply count the number of posts
        # between 100 and 300 and test.
        with self.subTest('Test filter on field `num_views` '
                          'using `range` lookup'):
            _count = 0
            for _p in self.all_posts:
                if 100 <= _p.num_views <= 300:
                    _count += 1
            self.__test_filter_number_lookups(
                '{%s: "%s", %s: "%s"}' % (LOWER, '100', UPPER, '300'),
                _count,
                lookup=LOOKUP_FILTER_RANGE
            )

    def test_all(self):
        """Test all.

        Since we don't write in specific tests, it's more efficient to run
        them all from a single method in order to save on speed ups between
        tests.
        """
        self._test_filter_term_terms_lookup()
        self._test_filter_prefix_starts_ends_with_contains_wildcard_lookups()
        self._test_filter_exclude_lookup()
        self._test_filter_exists_is_null_lookups()
        self._test_filter_gt_gte_lt_lte_range_lookups()


if __name__ == '__main__':
    unittest.main()
