Settings
========
Defaults are:

.. code-block:: python

    DEFAULTS = {
    "SCHEMA": None,
    "SCHEMA_OUTPUT": "schema.json",
    "SCHEMA_INDENT": 2,
    # "MIDDLEWARE": (),
    # Set to True if the connection fields must have
    # either the first or last argument
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": False,
    # Max items returned in ConnectionFields / FilterConnectionFields
    "RELAY_CONNECTION_MAX_LIMIT": 100,
    "LOGGING_LEVEL": logging.ERROR,
}

See the example below to get a grasp on how to override:

.. code-block:: python

    import json
    import logging
    import os

    DEFAULTS = {
        "SCHEMA": None,
        "SCHEMA_OUTPUT": "schema.json",
        "SCHEMA_INDENT": 2,
        # Set to True if the connection fields must have
        # either the first or last argument
        "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": False,
        # Max items returned in ConnectionFields / FilterConnectionFields
        "RELAY_CONNECTION_MAX_LIMIT": 100,
        "LOGGING_LEVEL": logging.DEBUG,
    }

    os.environ.setdefault(
        "GRAPHENE_ELASTIC",
        json.dumps(DEFAULTS)
    )
