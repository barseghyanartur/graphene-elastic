from importlib import reload
import json
import logging
import os
import unittest

from graphene_elastic import settings

__title__ = 'graphene_elastic.tests.test_settings'
__author__ = 'Artur Barseghyan'
__copyright__ = 'Copyright (c) 2019-2020 Artur Barseghyan'
__license__ = 'GPL-2.0-only OR LGPL-2.1-or-later'
__all__ = ('SettingsTest',)


DEFAULTS = {
    "SCHEMA": None,
    "SCHEMA_OUTPUT": "schema.json",
    "SCHEMA_INDENT": 2,
    # "MIDDLEWARE": ("apps.middleware.timing_middleware",),
    # Set to True if the connection fields must have
    # either the first or last argument
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": False,
    # Max items returned in ConnectionFields / FilterConnectionFields
    "RELAY_CONNECTION_MAX_LIMIT": 200,
    "LOGGING_LEVEL": logging.DEBUG,
}


class SettingsTest(unittest.TestCase):
    """
    Tests of ``graphene_elastic.settings`` module.
    """
    def setUp(self):
        pass

    def test_middleware_as_tuple(self):
        """Test middleware settings."""
        defaults = dict(DEFAULTS)

        defaults.update({"MIDDLEWARE": ("apps.middleware.timing_middleware",)})
        os.environ.update({"GRAPHENE_ELASTIC": json.dumps(defaults)})
        reload(settings)

        for middleware in settings.graphene_settings.MIDDLEWARE:
            self.assertTrue(callable(middleware))

    def test_middleware_as_str(self):
        """Test middleware settings."""
        defaults = dict(DEFAULTS)

        defaults.update({"MIDDLEWARE": "apps.middleware.timing_middleware"})
        os.environ.update({"GRAPHENE_ELASTIC": json.dumps(defaults)})
        reload(settings)

        self.assertTrue(callable(settings.graphene_settings.MIDDLEWARE))


if __name__ == "__main__":
    unittest.main()
