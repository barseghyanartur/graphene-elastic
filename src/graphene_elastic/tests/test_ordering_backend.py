import time
import unittest
import factories
from .base import BaseGrapheneElasticTestCase
from ..filter_backends.queries import Direction

__all__ = (
    'OrderingBackendElasticTestCase',
)


class OrderingBackendElasticTestCase(BaseGrapheneElasticTestCase):

    def setUp(self):
        super(OrderingBackendElasticTestCase, self).setUp()

        # Important thing to know about the factories.
        # The `PostFactory` factory has `num_views` between 0 and 1_000.
        # The `ManyViewsPostFactory` factory has `num_views` between
        # 2_000 and 10_000.
        self.num_elastic_posts = 4
        self.elastic_posts = factories.PostFactory.create_batch(
            self.num_elastic_posts,
            category='Elastic',
            tags=None
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
        self.all_posts = (
            self.elastic_posts + self.django_posts + self.python_posts
        )

        time.sleep(3)

    def _test_ordering(self, field, direction):
        """Test filter text lookups (on field `category`).

        :param field:
        :param direction:
        :return:
        """
        _query = """
        {
          allPostDocuments(ordering:{%s:%s}) {
            edges {
              node {
                category
                title
                content
                numViews
                tags
              }
            }
          }
        }
        """ % (field, direction.name)
        print(_query)
        executed = self.client.execute(_query)
        fields_values_sorted = []
        for edge in executed['data']['allPostDocuments']['edges']:
            field_value = edge.get('node', {}).get(field, None)
            fields_values_sorted.append(field_value)

        sorted_values = sorted(fields_values_sorted)
        if direction == Direction.DESC:
            sorted_values = reversed(sorted_values)

        self.assertEqual(sorted_values, fields_values_sorted)

    def test_ordering(self):
        """"Test ordering on fields `title`.

        :return:
        """
        with self.subTest('Test ordering on field `title` ascending'):
            self._test_ordering(
                'title',
                Direction.ASC
            )

        with self.subTest('Test ordering on field `title` descending'):
            self._test_ordering(
                'title',
                Direction.ASC
            )


if __name__ == '__main__':
    unittest.main()
