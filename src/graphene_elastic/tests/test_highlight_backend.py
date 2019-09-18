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

        self.beast = "Jabberwocky"
        self.num_beast_posts = 5
        self.beast_posts = factories.PostFactory.create_batch(
            self.num_beast_posts
        )
        for _post in self.beast_posts:
            _post.title = "{} {} {}".format(
                self.faker.word(),
                self.beast,
                self.faker.word()
            )
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

    def __check_values(self, edges, stack):
        for node in edges:
            for key, value in stack.items():
                if key in node['node']['highlight']:
                    self.assertIn(value, node['node']['highlight'][key][0])

    def __test_search_content(self, search, num_posts, stack):
        """Test search.

        content:{%s:"%s"}

        :param num_posts:
        :return:
        """
        query = """
        query {
          allPostDocuments(search:%s) {
            edges {
              node {
                category
                title
                highlight
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
            stack
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
                {
                    'title': '<b>{}</b>'.format(self.alice),
                    'content': '<em>{}</em>'.format(self.alice),
                }
            )
        with self.subTest('Test search the content on term "Elastic"'):
            self.__test_search_content(
                '{content:{%s:"%s"}}' % (VALUE, self.beast),
                self.num_beast_posts,
                {
                    'title': '<b>{}</b>'.format(self.beast),
                    'content': '<em>{}</em>'.format(self.beast),
                }
            )

        # Covering all field lookups: `search:{query:"Another"}`
        with self.subTest('Test search the content on term "Django"'):
            self.__test_search_content(
                '{%s:"%s"}' % (ALL, self.alice),
                self.num_alice_posts,
                {
                    'title': '<b>{}</b>'.format(self.alice),
                    'content': '<em>{}</em>'.format(self.alice),
                }
            )

        with self.subTest('Test search the content on term "Elastic"'):
            self.__test_search_content(
                '{%s:"%s"}' % (ALL, self.beast),
                self.num_beast_posts,
                {
                    'title': '<b>{}</b>'.format(self.beast),
                    'content': '<em>{}</em>'.format(self.beast),
                }
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
