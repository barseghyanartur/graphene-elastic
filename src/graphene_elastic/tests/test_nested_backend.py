import datetime
import unittest

from graphene.utils.str_converters import to_camel_case
import factories
from ..constants import (
    LOOKUP_FILTER_TERM,
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_EXISTS,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_WILDCARD,
    # LOOKUP_FILTER_REGEXP,
    # LOOKUP_FILTER_FUZZY,
    # LOOKUP_FILTER_TYPE,
    LOOKUP_FILTER_GEO_DISTANCE,
    LOOKUP_FILTER_GEO_POLYGON,
    LOOKUP_FILTER_GEO_BOUNDING_BOX,
    LOOKUP_QUERY_CONTAINS,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_STARTSWITH,
    LOOKUP_QUERY_ENDSWITH,
    LOOKUP_QUERY_ISNULL,
    LOOKUP_QUERY_EXCLUDE,
    VALUE,
    LOWER,
    UPPER,
)
from .base import BaseGrapheneElasticTestCase

__all__ = ("NestedFilterBackendElasticTestCase",)


class NestedFilterBackendElasticTestCase(BaseGrapheneElasticTestCase):
    def setUp(self):
        super(NestedFilterBackendElasticTestCase, self).setUp()

        # Important thing to know about the factories.
        # The `PostFactory` factory has `num_views` between 0 and 1_000.
        # The `ManyViewsPostFactory` factory has `num_views` between
        # 2_000 and 10_000.
        self.num_elastic_posts = 4
        self.elastic_posts = factories.PostFactory.create_batch(
            self.num_elastic_posts,
            category="Elastic",
            tags=None,
            created_at=self.faker.date_between(
                start_date="+1d", end_date="+30d"
            ),
        )
        for _post in self.elastic_posts:
            _post.save()

        self.num_django_posts = 3
        self.django_posts = factories.PostFactory.create_batch(
            self.num_django_posts,
            category="Django",
            created_at=self.faker.date_between(
                start_date="+1d", end_date="+30d"
            )
        )
        for _post in self.django_posts:
            _post.save()

        self.num_python_posts = 2
        self.python_posts = factories.ManyViewsPostFactory.create_batch(
            self.num_python_posts,
            category="Python",
            created_at=self.faker.date_between(
                start_date="-30d", end_date="-1d"
            ),
        )
        for _post in self.python_posts:
            _post.save()

        self.num_all_posts = (
            self.num_elastic_posts
            + self.num_django_posts
            + self.num_python_posts
        )
        self.all_posts = (
            self.elastic_posts + self.django_posts + self.python_posts
        )

        self.num_future_posts = self.num_elastic_posts + self.num_django_posts
        self.num_past_posts = self.num_python_posts
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")

        self.sleep()

    def __test_filter_text_lookups(
        self,
        query,
        num_posts,
        lookup=VALUE,
        field="comments",
        sub_field="content",
    ):
        """Test filter text lookups (on field `comments`).

        :param query:
        :param num_posts:
        :param field:
        :return:
        """
        _query = """
        query {
            allPostDocuments(nested:{%s:{%s:{%s:%s}}}){
                edges{
                    node{
                        comments
                    }
                }
            }
        }
        """ % (
            field,
            sub_field,
            lookup,
            query,
        )

        print(_query)
        executed = self.client.execute(_query)
        print(len(executed["data"]["allPostDocuments"]["edges"]))
        self.assertEqual(
            len(executed["data"]["allPostDocuments"]["edges"]), num_posts
        )

    def _test_filter_nested_contains_lookup(self):
        """ "Test filter contains` lookups (on field `comments`)"""
        self.__test_filter_text_lookups('"fear"', self.num_django_posts, LOOKUP_QUERY_CONTAINS)

    def _test_filter_nested_terms_lookup(self):
        """Test filter on field `comments` "Elastic" using`terms` lookup"""
        self.__test_filter_text_lookups('["fear"]', self.num_django_posts, LOOKUP_FILTER_TERMS)

    def _test_filter_nested_term_lookup(self):
        """Test filter on field `comments` "Elastic" using `terms` lookup"""
        self.__test_filter_text_lookups('"fear"', self.num_django_posts, LOOKUP_FILTER_TERM)

    def _test_filter_nested_range_lookup(self):
        pass

    def test_all(self):
        self._test_filter_nested_contains_lookup()
        self._test_filter_nested_range_lookup()
        self._test_filter_nested_terms_lookup()
        self._test_filter_nested_term_lookup()


if __name__ == "__main__":
    unittest.main()
