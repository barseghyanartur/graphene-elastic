import unittest
import time
import factories
from .base import BaseGrapheneElasticTestCase
from ..constants import ALL, VALUE

__all__ = (
    'FacetedSearchBackendElasticTestCase',
)


class FacetedSearchBackendElasticTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(FacetedSearchBackendElasticTestCase, self).setUp()
        self.alice = "Alice"
        self.alice_category = 'Delusional'
        self.num_alice_posts = 9
        self.alice_posts = factories.PostFactory.create_batch(
            self.num_alice_posts,
            category=self.alice_category

        )
        for _post in self.alice_posts:
            _post.content = "{} {} {}".format(
                self.faker.paragraph(),
                self.alice,
                self.faker.paragraph()
            )
            _post.save()

        self.beast = "Jabberwocky"
        self.beast_category = 'Insanity'
        self.num_beast_posts = 5
        self.beast_posts = factories.PostFactory.create_batch(
            self.num_beast_posts,
            category=self.beast_category,
        )
        for _post in self.beast_posts:
            _post.content = "{} {} {}".format(
                self.faker.paragraph(),
                self.beast,
                self.faker.paragraph()
            )
            _post.save()

        self.num_other_posts = 40
        self.other_posts = factories.PostFactory.create_batch(
            self.num_other_posts
        )
        for _post in self.other_posts:
            _post.save()

        time.sleep(2)

    def __test_faceted_search_no_facets_args(self):
        """Test faceted search.

        :param num_posts:
        :return:
        """
        query = """
        query {
          allPostDocuments {
            facets
            edges {
              node {
                category
                title
                comments
              }
            }
          }
        }
        """
        print(query)
        executed = self.client.execute(query)
        data = executed.get('data', {}).get('allPostDocuments', {})
        self.assertIn('facets', data)
        self.assertIn('tags', data['facets'])
        self.assertNotIn('category', data['facets'])
        self.assertIn('aggs', data['facets']['tags'])
        self.assertIn('buckets', data['facets']['tags']['aggs'])

    def __test_faceted_search_with_facets_args(self):
        """Test faceted search.

        :return:
        """
        query = """
        query {
          allPostDocuments(facets:[category]) {
            facets
            edges {
              node {
                category
                title
                comments
              }
            }
          }
        }
        """
        print(query)
        executed = self.client.execute(query)
        data = executed.get('data', {}).get('allPostDocuments', {})
        self.assertIn('facets', data)
        self.assertIn('tags', data['facets'])
        self.assertIn('category', data['facets'])
        self.assertIn('aggs', data['facets']['category'])
        self.assertIn('aggs', data['facets']['tags'])
        self.assertIn('buckets', data['facets']['category']['aggs'])
        self.assertIn('buckets', data['facets']['tags']['aggs'])

        buckets = data['facets']['category']['aggs']['buckets']
        doc_counts = {_d['key']: _d['doc_count'] for _d in buckets}
        self.assertEqual(
            doc_counts.get(self.alice_category),
            self.num_alice_posts
        )
        self.assertEqual(
            doc_counts.get(self.beast_category),
            self.num_beast_posts
        )

    def _test_faceted_search(self):
        """"Test search content.

        :return:
        """
        # Covering default facets (no specific facets enabled)
        with self.subTest('Test empty facets'):
            self.__test_faceted_search_no_facets_args()

        # Covering specific facets (that aren't enabled by default)
        with self.subTest('Test given facets'):
            self.__test_faceted_search_with_facets_args()

    def test_all(self):
        """Test all.

        Since we don't write in specific tests, it's more efficient to run
        them all from a single method in order to save on speed ups between
        tests.
        """
        self._test_faceted_search()


if __name__ == '__main__':
    unittest.main()
