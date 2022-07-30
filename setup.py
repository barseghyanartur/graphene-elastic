from setuptools import find_packages, setup

setup(
    name="graphene-elastic",
    version="0.8",
    description="Graphene Elasticsearch/OpenSearch (DSL) integration",
    long_description=open("README.rst").read(),
    url="https://github.com/barseghyanartur/graphene-elastic",
    project_urls={
        "Bug Tracker": "https://github.com/barseghyanartur/graphene-elastic/"
                       "issues",
        "Documentation": "https://graphene-elastic.readthedocs.io/",
        "Source Code": "https://github.com/barseghyanartur/graphene-elastic/",
        "Changelog": "https://graphene-elastic.readthedocs.io/"
                     "en/latest/changelog.html",
    },
    author="Artur Barseghyan",
    author_email="artur.barseghyan@gmail.com",
    license="GPL 2.0/LGPL 2.1",  # GPL-2.0-only OR LGPL-2.1-or-later
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="api graphql protocol rest relay graphene anysearch "
    "elasticsearch elasticsearch-dsl opensearch opensearch-dsl",
    package_dir={"": "src"},
    packages=find_packages(
        where="./src",
        exclude=["tests"]
    ),
    install_requires=[
        "graphene>=2.1.3,<3",
        # "elasticsearch>=6.0",
        # "elasticsearch-dsl>=6.0",
        "singledispatch>=3.4.0.3",
        "iso8601>=0.1.12",
        "stringcase",
        'typing;python_version<"3.7"',  # Used in Python < 3.6 dist
        "anysearch>=0.2.1",
    ],
    extras_require={
        "elasticsearch": [
            "elasticsearch>=6.0",
            "elasticsearch-dsl>=6.0<8.0",
        ],
        "opensearch": [
            "opensearch-py",
            "opensearch-dsl",
        ],
    },
    python_requires=">=3.6",
    zip_safe=True,
    tests_require=[
        "pytest>=3.3.2",
        "mock",
    ],
    include_package_data=True,
)
