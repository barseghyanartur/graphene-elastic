import logging
import time
import unittest
from faker import Faker
from graphene.test import Client
from elasticsearch import Elasticsearch
from schema import schema
from search_index.documents.settings import (
    BLOG_POST_DOCUMENT_NAME,
    SITE_USER_DOCUMENT_NAME,
    ELASTICSEARCH_CONNECTION
)
from search_index.documents import Post, User

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
        self.create_elasticsearch_indexes()

    @classmethod
    def sleep(cls, value=3):
        time.sleep(value)

    def remove_elasticsearch_indexes(self):
        """"""
        for _index in [BLOG_POST_DOCUMENT_NAME, SITE_USER_DOCUMENT_NAME]:
            try:
                _res = self.elasticsearch.indices.delete(_index)
            except Exception as err:
                print(err)

    def create_elasticsearch_indexes(self):
        """"""
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
