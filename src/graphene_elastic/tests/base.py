import logging
import time
import unittest
from faker import Faker
from graphene.test import Client
from anysearch.search import AnySearch as Elasticsearch
from schema import schema
from search_index.documents.settings import (
    BLOG_POST_DOCUMENT_NAME,
    SITE_USER_DOCUMENT_NAME,
    ELASTICSEARCH_CONNECTION
)
from search_index.documents import Post, User
from ..logging import logger

__all__ = (
    'BaseGrapheneElasticTestCase',
)


LOGGER = logging.getLogger(__name__)


class BaseGrapheneElasticTestCase(unittest.TestCase):
    """Base graphene-elastic test case."""

    @classmethod
    def setUpClass(cls):
        cls.client = Client(schema)
        cls.elasticsearch = Elasticsearch(**ELASTICSEARCH_CONNECTION)
        cls.faker = Faker()

    def setUp(self):
        super(BaseGrapheneElasticTestCase, self).setUp()
        self.remove_elasticsearch_indexes()
        self.sleep()
        self.create_elasticsearch_indexes()
        self.sleep()

    def tearDown(self):
        super(BaseGrapheneElasticTestCase, self).tearDown()
        self.remove_elasticsearch_indexes()
        self.sleep()

    @classmethod
    def sleep(cls, value=3):
        time.sleep(value)

    def remove_elasticsearch_index(self, index_name, retry=0):
        try:
            _res = self.elasticsearch.indices.delete(index_name)
        except Exception as err:
            logger.debug_json(err)
            if retry < 3:
                self.remove_elasticsearch_index(index_name, retry + 1)

    def remove_elasticsearch_indexes(self):
        """Remove all ES indexes."""
        for _index in [BLOG_POST_DOCUMENT_NAME, SITE_USER_DOCUMENT_NAME]:
            self.remove_elasticsearch_index(_index)

    def create_elasticsearch_indexes(self):
        """Create ES indexes."""
        try:
            # Create the mappings in Elasticsearch
            User.init()
        except Exception as err:
            LOGGER.error(err)

        try:
            # Create the mappings in Elasticsearch
            Post.init()
        except Exception as err:
            LOGGER.error(err)
