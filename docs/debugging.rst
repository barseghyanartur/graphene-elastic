Debugging
=========
Logging queries to console
--------------------------
The ``LOGGING_LEVEL`` key represents the logging level (defaults to
``logging.ERROR``). Override if needed.

Typical development setup would be:

.. code-block:: python

    import json
    import logging
    import os

    DEFAULTS = {
        # ...
        "LOGGING_LEVEL": logging.DEBUG,
        # ...
    }

    os.environ.setdefault(
        "GRAPHENE_ELASTIC",
        json.dumps(DEFAULTS)
    )
