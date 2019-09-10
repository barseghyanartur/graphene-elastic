#!/usr/bin/env python
import os
import sys

import pytest


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
