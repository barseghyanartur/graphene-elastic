import unittest
import factories
from .base import BaseGrapheneElasticTestCase
from ..constants import ALL, VALUE

__all__ = ("SimpleQueryStringBackendElasticTestCase",)


class SimpleQueryStringBackendElasticTestCase(BaseGrapheneElasticTestCase):
    def setUp(self):
        super(SimpleQueryStringBackendElasticTestCase, self).setUp()
        self.alice = "Alice"
        self.num_alice_posts = 9
        self.alice_posts = factories.PostFactory.create_batch(
            self.num_alice_posts
        )
        for _post in self.alice_posts:
            _post.content = "{} {} {}".format(
                self.faker.paragraph(), self.alice, self.faker.paragraph()
            )
            _post.save()

        self.beast = "Jabberwocky"
        self.num_beast_posts = 5
        self.beast_posts = factories.PostFactory.create_batch(
            self.num_beast_posts
        )
        for _post in self.beast_posts:
            _post.content = "{} {} {}".format(
                self.faker.paragraph(), self.beast, self.faker.paragraph()
            )
            _post.save()

        self.num_other_posts = 40
        self.other_posts = factories.PostFactory.create_batch(
            self.num_other_posts
        )
        for _post in self.other_posts:
            _post.save()

        self.sleep(2)

    def __test_search_content(self, search, num_posts):
        """Test search.

        :param num_posts:
        :return:
        """
        query = (
            """
        query {
          allPostDocuments(simpleQueryString:%s) {
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
            % search
        )
        print(query)
        executed = self.client.execute(query)
        self.assertEqual(
            len(executed["data"]["allPostDocuments"]["edges"]), num_posts
        )

    def _test_search_content(self):
        """ "Test search content.

        :return:
        """
        # Covering specific field lookups: `search:{title:{value:"Another"}}`
        with self.subTest('Test search the content on term "Alice"'):
            self.__test_search_content(
                '"%s"' % self.alice,
                self.num_alice_posts,
            )
        with self.subTest('Test search the content on term "Jabberwocky"'):
            self.__test_search_content(
                '"%s"' % self.beast,
                self.num_beast_posts,
            )

        with self.subTest(
            'Test search the content on term "Alice Jabberwocky"'
        ):
            self.__test_search_content(
                '"%s %s"' % (self.alice, self.beast),
                self.num_alice_posts + self.num_beast_posts,
            )

    def test_all(self):
        """Test all.

        Since we don't write in specific tests, it's more efficient to run
        them all from a single method in order to save on speed ups between
        tests.
        """
        self._test_search_content()


if __name__ == "__main__":
    unittest.main()
