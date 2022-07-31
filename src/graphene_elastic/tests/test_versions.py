import unittest
import mock
from importlib import reload

from anysearch import check_if_package_is_installed

__author__ = 'Artur Barseghyan'
__copyright__ = '2019-2022 Artur Barseghyan'
__license__ = 'GPL-2.0-only OR LGPL-2.1-or-later'
__all__ = ('VersionsTest',)


class VersionsTest(unittest.TestCase):
    """
    Tests of ``graphene_elastic.versions`` module.
    """
    def setUp(self):
        pass

    @unittest.skipUnless(
        check_if_package_is_installed("elasticsearch-dsl"),
        "elasticsearch-dsl is not installed",
    )
    @mock.patch('elasticsearch_dsl.__version__', [6, 3, 0])
    def test_elasticsearch_dsl_6_3_0(self):
        """
        Tests as if we were using elasticsearch_dsl==6.3.0.
        """
        from graphene_elastic import versions
        reload(versions)

        # Exact version matching
        self.assertFalse(versions.ELASTICSEARCH_7_0)
        self.assertTrue(versions.ELASTICSEARCH_6_3)
        self.assertFalse(versions.ELASTICSEARCH_6_2)
        self.assertFalse(versions.ELASTICSEARCH_5_4)
        self.assertFalse(versions.ELASTICSEARCH_2_0)
        self.assertFalse(versions.ELASTICSEARCH_6_2)

        # Less than or equal matching
        self.assertFalse(versions.ELASTICSEARCH_LTE_2_0)
        self.assertFalse(versions.ELASTICSEARCH_LTE_2_2)
        self.assertFalse(versions.ELASTICSEARCH_LTE_5_0)
        self.assertFalse(versions.ELASTICSEARCH_LTE_5_3)
        self.assertFalse(versions.ELASTICSEARCH_LTE_6_0)
        self.assertTrue(versions.ELASTICSEARCH_LTE_6_3)
        self.assertTrue(versions.ELASTICSEARCH_LTE_7_0)
        self.assertTrue(versions.ELASTICSEARCH_LTE_8_0)

        # Greater than or equal matching
        self.assertTrue(versions.ELASTICSEARCH_GTE_2_0)
        self.assertTrue(versions.ELASTICSEARCH_GTE_2_2)
        self.assertTrue(versions.ELASTICSEARCH_GTE_5_0)
        self.assertTrue(versions.ELASTICSEARCH_GTE_5_3)
        self.assertTrue(versions.ELASTICSEARCH_GTE_6_0)
        self.assertTrue(versions.ELASTICSEARCH_GTE_6_3)
        self.assertFalse(versions.ELASTICSEARCH_GTE_7_0)
        self.assertFalse(versions.ELASTICSEARCH_GTE_8_0)

    @unittest.skipUnless(
        check_if_package_is_installed("elasticsearch-dsl"),
        "elasticsearch-dsl is not installed",
    )
    @mock.patch('elasticsearch_dsl.__version__', [7, 0, 0])
    def test_elasticsearch_dsl_7_0_0(self):
        """
        Tests as if we were using elasticsearch_dsl==7.0.0.
        """
        from graphene_elastic import versions
        reload(versions)

        # Exact version matching
        self.assertTrue(versions.ELASTICSEARCH_7_0)
        self.assertFalse(versions.ELASTICSEARCH_6_3)
        self.assertFalse(versions.ELASTICSEARCH_6_2)
        self.assertFalse(versions.ELASTICSEARCH_5_4)
        self.assertFalse(versions.ELASTICSEARCH_2_0)
        self.assertFalse(versions.ELASTICSEARCH_6_2)

        # Less than or equal matching
        self.assertFalse(versions.ELASTICSEARCH_LTE_2_0)
        self.assertFalse(versions.ELASTICSEARCH_LTE_2_2)
        self.assertFalse(versions.ELASTICSEARCH_LTE_5_0)
        self.assertFalse(versions.ELASTICSEARCH_LTE_5_3)
        self.assertFalse(versions.ELASTICSEARCH_LTE_6_0)
        self.assertFalse(versions.ELASTICSEARCH_LTE_6_3)
        self.assertTrue(versions.ELASTICSEARCH_LTE_7_0)
        self.assertTrue(versions.ELASTICSEARCH_LTE_8_0)

        # Greater than or equal matching
        self.assertTrue(versions.ELASTICSEARCH_GTE_2_0)
        self.assertTrue(versions.ELASTICSEARCH_GTE_2_2)
        self.assertTrue(versions.ELASTICSEARCH_GTE_5_0)
        self.assertTrue(versions.ELASTICSEARCH_GTE_5_3)
        self.assertTrue(versions.ELASTICSEARCH_GTE_6_0)
        self.assertTrue(versions.ELASTICSEARCH_GTE_6_3)
        self.assertTrue(versions.ELASTICSEARCH_GTE_7_0)
        self.assertFalse(versions.ELASTICSEARCH_GTE_8_0)


if __name__ == "__main__":
    unittest.main()
