import unittest
import time
import factories
from .base import BaseGrapheneElasticTestCase

__all__ = (
    'FilterBackendElasticTestCase',
)


class FilterBackendElasticTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(FilterBackendElasticTestCase, self).setUp()
        self.num_elastic_posts = 10
        self.elastic_posts = factories.PostFactory.create_batch(
            self.num_elastic_posts,
            category='Elastic'
        )
        for _post in self.elastic_posts:
            _post.save()

        self.num_django_posts = 8
        self.django_posts = factories.PostFactory.create_batch(
            self.num_django_posts,
            category='Django'
        )
        for _post in self.django_posts:
            _post.save()

        time.sleep(2)

    def _test_filter_category_term(self, term, num_posts):
        """Test filter.

        :param term:
        :param num_posts:
        :return:
        """
        query = """
        query {
          allPostDocuments(filter:{category:{query:["%s"]}}) {
            edges {
              node {
                category
                title
                comments
              }
            }
          }
        }
        """ % term
        executed = self.client.execute(query)
        self.assertEqual(
            len(executed['data']['allPostDocuments']['edges']),
            num_posts
        )

    def test_filter_category_terms(self):
        """"Test filter category term.

        :return:
        """
        with self.subTest('Test filter on category on term "Django"'):
            self._test_filter_category_term('Django', self.num_django_posts)

        with self.subTest('Test filter on category on term "Elastic"'):
            self._test_filter_category_term('Elastic', self.num_elastic_posts)


if __name__ == '__main__':
    unittest.main()
