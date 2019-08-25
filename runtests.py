#!/usr/bin/env python
import os
import sys

import pytest


def main():
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.testing")
    os.environ.setdefault(
        "GRAPHENE_ELASTIC_EXAMPLE_BLOG_POST_DOCUMENT_NAME",
        "test_blog_post"
    )
    os.environ.setdefault(
        "GRAPHENE_ELASTIC_EXAMPLE_SITE_USER_DOCUMENT_NAME",
        "test_site_user"
    )
    sys.path.insert(0, "src")
    sys.path.insert(0, "examples")
    # sys.path.insert(0, "examples")
    return pytest.main()


if __name__ == '__main__':
    sys.exit(main())
