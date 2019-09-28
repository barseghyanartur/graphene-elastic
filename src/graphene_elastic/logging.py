import json
import logging
import sys

from .settings import graphene_settings

__title__ = 'graphene_elastic.logging'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'logger',
)

# Logger
logger = logging.getLogger(__name__)

# Get logging level. If not set, ERROR by default
try:
    logging_level = int(graphene_settings.LOGGING_LEVEL)
except ValueError as err:
    logging_level = logging.ERROR

# Set logging level for the logger
logger.setLevel(logging_level)

# This might be more flexible
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging_level)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def debug_json(msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'DEBUG'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
    """
    try:
        msg = json.dumps(msg)
    except Exception:
        pass
    return logger.debug(msg, *args, **kwargs)


logger.debug_json = debug_json
