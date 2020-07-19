import unittest
import factories
from .base import BaseGrapheneElasticTestCase
from ..constants import ALL, VALUE

__all__ = (
    'ScoreBackendElasticTestCase',
)


class ScoreBackendElasticTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(ScoreBackendElasticTestCase, self).setUp()
        self.alice = "Alice"
        self.num_alice_posts = 9
        self.alice_posts = factories.PostFactory.create_batch(
            self.num_alice_posts
        )
        for _post in self.alice_posts:
            _post.title = "{} {} {}".format(
                self.faker.word().title(),
                self.alice,
                self.faker.word()
            )
            _post.content = "{} {} {}".format(
                self.faker.paragraph(),
                self.alice,
                self.faker.paragraph()
            )
            _post.save()

        self.sleep(2)

    def __check_values(self, edges):
        for node in edges:
            self.assertIn('score', node['node'])

    def __test_search_content(self, search, num_posts):
        """Test search.

        content:{%s:"%s"}

        :param num_posts:
        :return:
        """
        query = """
        query {
          allPostDocuments(search:%s, ordering:{score:DESC}) {
            edges {
              node {
                category
                title
                score
              }
            }
          }
        }
        """ % search
        print(query)
        executed = self.client.execute(query)
        self.assertEqual(
            len(executed['data']['allPostDocuments']['edges']),
            num_posts
        )
        self.__check_values(executed['data']['allPostDocuments']['edges'])
        return executed

    def _test_search_content(self):
        """"Test search content.

        :return:
        """
        # Covering all field lookups: `search:{query:"Alice"}`
        with self.subTest('Test search the content on term "Alice"'):
            self.__test_search_content(
                '{%s:"%s"}' % (ALL, self.alice),
                self.num_alice_posts
            )

    def test_all(self):
        """Test all.

        Since we don't write in specific tests, it's more efficient to run
        them all from a single method in order to save on speed ups between
        tests.
        """
        self._test_search_content()


if __name__ == '__main__':
    unittest.main()
