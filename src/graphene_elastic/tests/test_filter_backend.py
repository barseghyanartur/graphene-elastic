import unittest
import time
import factories
from ..constants import VALUE
from .base import BaseGrapheneElasticTestCase

__all__ = (
    'FilterBackendElasticTestCase',
)


class FilterBackendElasticTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(FilterBackendElasticTestCase, self).setUp()
        self.num_elastic_posts = 4
        self.elastic_posts = factories.PostFactory.create_batch(
            self.num_elastic_posts,
            category='Elastic'
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

        time.sleep(2)

    def _test_filter_category_lookups(self,
                                      query,
                                      num_posts,
                                      lookup=VALUE):
        """Test filter category lookups.

        :param query:
        :param num_posts:
        :return:
        """
        _query = """
        query {
          allPostDocuments(filter:{category:{%s:"%s"}}) {
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
        """ % (lookup, query)
        print(_query)
        executed = self.client.execute(_query)
        self.assertEqual(
            len(executed['data']['allPostDocuments']['edges']),
            num_posts
        )

    def test_filter_category_lookups(self):
        """"Test filter category lookups.

        :return:
        """
        with self.subTest('Test filter on category on term "Django" '
                          'using default lookup'):
            self._test_filter_category_lookups(
                'Django',
                self.num_django_posts
            )

        with self.subTest('Test filter on category on term "Django" '
                          'using `term` lookup'):
            self._test_filter_category_lookups(
                'Django',
                self.num_django_posts,
                lookup='term'
            )

        with self.subTest('Test filter on category on term "Elastic" '
                          'using default lookup'):
            self._test_filter_category_lookups(
                'Elastic',
                self.num_elastic_posts
            )

        with self.subTest('Test filter on category on term "Elastic" '
                          'using `term` lookup'):
            self._test_filter_category_lookups(
                'Elastic',
                self.num_elastic_posts,
                'term'
            )

    def _test_filter_num_views_lookups(self,
                                       value,
                                       num_posts,
                                       lookup='gt'):
        """Test filter num_views lookups.

        :param value:
        :param num_posts:
        :param lookup:
        :return:
        """
        _query = """
        query {
          allPostDocuments(filter:{numViews:{%s:"%s"}}) {
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

    def test_filter_num_views_lookups(self):
        """"Test filter num_views lookups.

        :return:
        """
        with self.subTest('Test filter on num_views gt lookup'):
            self._test_filter_num_views_lookups(
                '0',
                self.num_all_posts
            )

        with self.subTest('Test filter on num_views gt lookup'):
            self._test_filter_num_views_lookups(
                '2000',
                self.num_python_posts
            )


if __name__ == '__main__':
    unittest.main()
