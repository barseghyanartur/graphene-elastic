#!/usr/bin/env python
from logging import config
import os
import sys

import pytest

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} '
                      '{thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'graphene_elastic': {
            'handlers': ['console'],
            'propagate': True,
        },
    },
}

config.dictConfig(LOGGING_CONFIG)


def main():
    os.environ.setdefault(
        "GRAPHENE_ELASTIC_EXAMPLE_BLOG_POST_DOCUMENT_NAME",
        "test_blog_post"
    )
    os.environ.setdefault(
        "GRAPHENE_ELASTIC_EXAMPLE_SITE_USER_DOCUMENT_NAME",
        "test_site_user"
    )
    os.environ.setdefault(
        "GRAPHENE_ELASTIC_EXAMPLE_FARM_ANIMAL_DOCUMENT_NAME",
        "test_farm_animal"
    )
    sys.path.insert(0, "src")
    sys.path.insert(0, "examples")
    return pytest.main()


if __name__ == '__main__':
    sys.exit(main())
