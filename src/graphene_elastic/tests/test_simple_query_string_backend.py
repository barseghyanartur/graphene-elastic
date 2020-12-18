import unittest
import uuid

import factories
from ..constants import ALL, VALUE
from ..logging import logger
from .base import BaseGrapheneElasticTestCase

__all__ = ("SimpleQueryStringBackendElasticTestCase",)


class SimpleQueryStringBackendElasticTestCase(BaseGrapheneElasticTestCase):
    def setUp(self):
        super(SimpleQueryStringBackendElasticTestCase, self).setUp()
        self.white_rabbit_partial = "White Rabbit is dead {}".format(
            uuid.uuid4()
        )
        self.alice = "Alice"
        self.num_alice_posts = 9
        self.alice_posts = factories.PostFactory.create_batch(
            self.num_alice_posts
        )
        for _counter, _post in enumerate(self.alice_posts):
            _partial = self.white_rabbit_partial if _counter == 0 else ''
            _post.content = "{} {} {} {}".format(
                self.faker.paragraph(),
                self.alice,
                self.faker.paragraph(),
                _partial
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
        logger.debug_json(query)
        executed = self.client.execute(query)
        self.assertEqual(
            len(executed["data"]["allPostDocuments"]["edges"]),
            num_posts,
            query
        )

    def _test_search_content(self):
        """ "Test search content.

        :return:
        """
        # Covering specific field lookups: `search:{title:{value:"Another"}}`
        with self.subTest('Test search the content on term: Alice'):
            self.__test_search_content(
                '"%s"' % self.alice,
                self.num_alice_posts,
            )

        with self.subTest('Test search the content on term: Jabberwocky'):
            self.__test_search_content(
                '"%s"' % self.beast,
                self.num_beast_posts,
            )

        with self.subTest(
            'Test search the content on term: Alice Jabberwocky'
        ):
            self.__test_search_content(
                '"%s %s"' % (self.alice, self.beast),
                self.num_alice_posts + self.num_beast_posts,
            )

        with self.subTest(
            'Test search the content on term: "White Rabbit" +Alice'
        ):
            self.__test_search_content(
                '"%s"' % "'{white_rabbit}' +{alice}".format(
                    white_rabbit=self.white_rabbit_partial,
                    alice=self.alice
                ),
                1,
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
