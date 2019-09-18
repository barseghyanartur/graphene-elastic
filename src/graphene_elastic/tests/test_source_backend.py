import unittest
import time
import factories
from .base import BaseGrapheneElasticTestCase
from ..constants import ALL, VALUE

__all__ = (
    'HighlightBackendElasticTestCase',
)


class HighlightBackendElasticTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(HighlightBackendElasticTestCase, self).setUp()
        self.alice = "Alice"
        self.num_alice_posts = 9
        self.alice_posts = factories.PostFactory.create_batch(
            self.num_alice_posts
        )
        for _post in self.alice_posts:
            _post.title = "{} {} {}".format(
                self.faker.word(),
                self.alice,
                self.faker.word()
            )
            _post.content = "{} {} {}".format(
                self.faker.paragraph(),
                self.alice,
                self.faker.paragraph()
            )
            _post.save()

        time.sleep(2)

    def __check_values(self, edges, stack, empty_stack):
        for node in edges:
            for key, value in node['node'].items():
                if key in stack:
                    self.assertIsNotNone(value)
                elif key in empty_stack:
                    self.assertIsNone(value)

    def __test_search_content(self, search, num_posts, stack, empty_stack):
        """Test search.

        content:{%s:"%s"}

        :param num_posts:
        :return:
        """
        query = """
        query {
          allPostDocuments(search:%s, source:[title, comments, id]) {
            edges {
              node {
                id
                title
                content
                category
                comments
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
        self.__check_values(
            executed['data']['allPostDocuments']['edges'],
            stack,
            empty_stack
        )
        return executed

    def _test_search_content(self):
        """"Test search content.

        :return:
        """
        # Covering specific field lookups: `search:{title:{value:"Another"}}`
        with self.subTest('Test search the content on term "Django"'):
            self.__test_search_content(
                '{content:{%s:"%s"}}' % (VALUE, self.alice),
                self.num_alice_posts,
                ['title', 'comments', 'id'],
                ['content', 'category']
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
