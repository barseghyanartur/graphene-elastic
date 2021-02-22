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
        self.num_elastic_comments = self.num_elastic_posts
        self.elastic_posts = factories.PostFactory.create_batch(
            self.num_elastic_posts,
            category="Elastic",
            tags=None,
            comments=factories.CommentFactory.create(author="Elastic", content="Elastic Comment", like_count=1000),
            created_at=self.faker.date_between(
                start_date="+1d", end_date="+30d"
            ),
        )
        for _post in self.elastic_posts:
            _post.save()

        self.num_django_posts = 3
        self.num_django_comments = self.num_django_posts
        self.django_posts = factories.PostFactory.create_batch(
            self.num_django_posts,
            category="Django",
            comments=factories.CommentFactory.create(author="Django", content="Django Comment", like_count=500),
            created_at=self.faker.date_between(
                start_date="+1d", end_date="+30d"
            )
        )
        for _post in self.django_posts:
            _post.save()

        self.num_python_posts = 2
        self.num_python_comments = self.num_python_posts
        self.python_posts = factories.ManyViewsPostFactory.create_batch(
            self.num_python_posts,
            category="Python",
            comments=factories.CommentFactory.create(author="Python", content="Python Comment", like_count=0),
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
        self.num_all_comments = (
            self.num_elastic_comments + self.num_django_comments + self.num_python_comments
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
            to_camel_case(field),
            to_camel_case(sub_field),
            to_camel_case(lookup),
            query,
        )

        executed = self.client.execute(_query)
        self.assertEqual(
            len(executed["data"]["allPostDocuments"]["edges"]), num_posts
        )

    def test_filter_contains_lookup(self):
        """Test filter contains."""
        with self.subTest("Test contains lookup on field `comments.content` with value `elastic` "):
            self.__test_filter_text_lookups('"elastic"', 0, LOOKUP_QUERY_CONTAINS)

        with self.subTest("Test contains lookup on field `comments.content` with value `django` "):
            self.__test_filter_text_lookups('"django"', self.num_django_comments, LOOKUP_QUERY_CONTAINS)

        with self.subTest("Test contains lookup on field `comments.content` with value `python` "):
            self.__test_filter_text_lookups('"python"', self.num_python_comments, LOOKUP_QUERY_CONTAINS)

    def test_filter_terms_lookup(self):
        """Test filter terms."""
        self.__test_filter_text_lookups('["django", "python"]', self.num_django_comments + self.num_python_comments, LOOKUP_FILTER_TERMS)

    def test_filter_term_lookup(self):
        """Test filter term."""
        self.__test_filter_text_lookups('"comment"', self.num_all_comments, LOOKUP_FILTER_TERM)

    # def test_filter_range_lookup(self):
    #     """Test filter range"""

    def test_filter_lt_lte_gt_gte_lookup(self):
        """Test filter on `lt`/`lte`/`gt`/`gte`"""
        _query = """
        query {{
            allPostDocuments(nested:{{
                comments:{{
                    likeCount:{params}
                    }}
                }}
            ){{
                edges{{
                    node{{
                        comments
                    }}
                }}
            }}
        }}
        """
        with self.subTest("Test filter lt"):
            executed = self.client.execute(_query.format(params=r"{lt:{int: 500}}"))
            self.assertEqual(
                len(executed["data"]["allPostDocuments"]["edges"]),
                self.num_python_comments
            )

        with self.subTest("Test filter lte"):
            executed = self.client.execute(_query.format(params=r"{lte:{int: 500}}"))
            self.assertEqual(
                len(executed["data"]["allPostDocuments"]["edges"]),
                self.num_python_comments + self.num_django_comments
            )
        
        with self.subTest("Test filter gt"):
            executed = self.client.execute(_query.format(params=r"{gt:{int: 500}}"))
            self.assertEqual(
                len(executed["data"]["allPostDocuments"]["edges"]),
                self.num_elastic_comments
            )

        with self.subTest("Test filter gte"):
            executed = self.client.execute(_query.format(params=r"{gte:{int: 500}}"))
            self.assertEqual(
                len(executed["data"]["allPostDocuments"]["edges"]),
                self.num_django_comments + self.num_elastic_comments
            )

    def test_filter_in_lookup(self):
        """Test filter on `in` lookup on field `comments`"""
        self.__test_filter_text_lookups('["django", "python"]', self.num_django_comments + self.num_python_comments, LOOKUP_QUERY_IN)

    def test_filter_is_null_lookup_true(self):
        """Test filter is_null true."""
        self.__test_filter_text_lookups('true', 0, LOOKUP_QUERY_ISNULL)

    def test_filter_is_null_lookup_false(self):
        """Test filter is_null false."""
        self.__test_filter_text_lookups('false', self.num_all_comments, LOOKUP_QUERY_ISNULL)

    def test_filter_exists_lookup_true(self):
        """Test filter exists true."""
        self.__test_filter_text_lookups('true', self.num_all_comments, LOOKUP_FILTER_EXISTS)

    def test_filter_exists_lookup_false(self):
        """Test filter exists."""
        self.__test_filter_text_lookups('false', 0, LOOKUP_FILTER_EXISTS)

    def test_filter_wildcard_lookup(self):
        """Test filter wildcard."""
        self.__test_filter_text_lookups('"*comment*"', self.num_all_comments, LOOKUP_FILTER_WILDCARD)

    def test_filter_exclude_lookup(self):
        """Test filter exclude."""
        self.__test_filter_text_lookups('"comment"', 0, LOOKUP_QUERY_EXCLUDE)

    def test_filter_startswith_lookup(self):
        """Test filter startswith."""
        self.__test_filter_text_lookups('"com"', self.num_all_comments, LOOKUP_QUERY_STARTSWITH)

    def test_filter_prefix_lookup(self):
        """Test filter prefix."""
        self.__test_filter_text_lookups('"com"', self.num_all_comments, LOOKUP_FILTER_PREFIX)

    def test_filter_endswith_lookup(self):
        """Test filter endswith."""
        self.__test_filter_text_lookups('"ment"', self.num_all_comments, LOOKUP_QUERY_ENDSWITH)

if __name__ == "__main__":
    unittest.main()
