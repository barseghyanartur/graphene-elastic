import unittest
import time
import factories
from .base import BaseGrapheneElasticTestCase
from ..constants import VALUE

__all__ = (
    'SearchBackendElasticTestCase',
)


class SearchBackendElasticTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(SearchBackendElasticTestCase, self).setUp()
        self.num_elastic_posts = 9
        self.elastic_posts = factories.PostFactory.create_batch(
            self.num_elastic_posts
        )
        for _post in self.elastic_posts:
            _post.content = "{} Elastic {}".format(
                self.faker.paragraph(),
                self.faker.paragraph()
            )
            _post.save()

        # TODO: Solve issue with failing tests if `num_django_posts` is
        # set to 20 (default number of Elastic results).
        self.num_django_posts = 5
        self.django_posts = factories.PostFactory.create_batch(
            self.num_django_posts
        )
        for _post in self.django_posts:
            _post.content = "{} Django {}".format(
                self.faker.paragraph(),
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

    def _test_search_content(self, term, num_posts, lookup=VALUE):
        """Test search.

        :param term:
        :param num_posts:
        :return:
        """
        query = """
        query {
          allPostDocuments(search:{content:{%s:"%s"}}) {
            edges {
              node {
                category
                title
                comments
              }
            }
          }
        }
        """ % (lookup, term)
        executed = self.client.execute(query)
        self.assertEqual(
            len(executed['data']['allPostDocuments']['edges']),
            num_posts
        )

    def test_search_content(self):
        """"Test search content.

        :return:
        """
        with self.subTest('Test search the content on term "Django"'):
            self._test_search_content('Django', self.num_django_posts)

        with self.subTest('Test search the content on term "Elastic"'):
            self._test_search_content('Elastic', self.num_elastic_posts)


if __name__ == '__main__':
    unittest.main()
