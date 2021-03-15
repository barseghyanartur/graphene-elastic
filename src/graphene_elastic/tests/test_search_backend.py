import logging
import unittest
import factories
from .base import BaseGrapheneElasticTestCase
from ..constants import ALL, VALUE

__all__ = (
    'SearchBackendElasticTestCase',
    'CompoundSearchBackendElasticTestCase',
)

logger = logging.getLogger(__name__)


class SearchBackendElasticTestCase(BaseGrapheneElasticTestCase):

    query_name = 'allPostDocuments'

    def setUp(self):
        super(SearchBackendElasticTestCase, self).setUp()

        self.alice = "Alice"
        self.num_alice_posts = 9
        self.alice_posts = factories.PostFactory.create_batch(
            self.num_alice_posts
        )
        for _post in self.alice_posts:
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
        # for _post in self.other_posts:
        #     _post.save()

        self.unique_term="Graphene"
        self.num_nested_posts = 20
        self.nested_posts = factories.PostFactory.create_batch(
            self.num_nested_posts
        )
        for _post in self.nested_posts:
            _post.comments=factories.CommentFactory.create(
                tag=self.unique_term,
            )
            _post.save()

        self.sleep(2)

    def __test_search_content(self, search, num_posts):
        """Test search.

        content:{%s:"%s"}

        :param num_posts:
        :return:
        """
        query = """
        query {
          %s(search:%s) {
            edges {
              node {
                category
                title
                comments{
                    author{
                        name
                    }
                    content
                    createdAt
                }
              }
            }
          }
        }
        """ % (self.query_name, search)
        logger.info(query)
        executed = self.client.execute(query)
        self.assertEqual(
            len(executed['data'][self.query_name]['edges']),
            num_posts,
            query
        )

    def _test_search_nested_tag(self):
        """Test search tag in nested field `comments`
        
        :return:
        """

        # Covering all field lookups `search:{comments:{query:"Graphene"}}`
        with self.subTest('Test search content in nested field `comments'
                          'on term "Python"'):
            self.__test_search_content(
                '{comments:{%s: "%s"}}' % (ALL, self.unique_term),
                self.num_nested_posts
            )
        
        # Covering specific field lookups `search:{comments:{tag:{value: "Graphene"}}}`
        with self.subTest('Test search content in nested field `comments`'
                          'on term "Python"'):
            self.__test_search_content(
                '{comments:{tag: {%s: "%s"} } }' % (VALUE, self.unique_term),
                self.num_nested_posts
            )


    def _test_search_content(self):
        """"Test search content.

        :return:
        """
        # Covering specific field lookups: `search:{title:{value:"Another"}}`
        with self.subTest('Test search the content on term "Django"'):
            self.__test_search_content(
                '{content:{%s:"%s"}}' % (VALUE, self.alice),
                self.num_alice_posts
            )
        with self.subTest('Test search the content on term "Elastic"'):
            self.__test_search_content(
                '{content:{%s:"%s"}}' % (VALUE, self.beast),
                self.num_beast_posts
            )

        # Covering all field lookups: `search:{query:"Another"}`
        with self.subTest('Test search the content on term "Django"'):
            self.__test_search_content(
                '{%s:"%s"}' % (ALL, self.alice),
                self.num_alice_posts
            )

        with self.subTest('Test search the content on term "Elastic"'):
            self.__test_search_content(
                '{%s:"%s"}' % (ALL, self.beast),
                self.num_beast_posts
            )

    def test_all(self):
        """Test all.

        Since we don't write in specific tests, it's more efficient to run
        them all from a single method in order to save on speed ups between
        tests.
        """
        self._test_search_content()
        self._test_search_nested_tag()


class CompoundSearchBackendElasticTestCase(SearchBackendElasticTestCase):

    query_name = 'allReadOnlyPostDocuments'


if __name__ == '__main__':
    unittest.main()
