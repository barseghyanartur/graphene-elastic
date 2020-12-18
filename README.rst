================
graphene-elastic
================
`Elasticsearch (DSL) <https://elasticsearch-dsl.readthedocs.io/en/latest/>`__
integration for `Graphene <http://graphene-python.org/>`__.

.. image:: https://img.shields.io/pypi/v/graphene-elastic.svg
   :target: https://pypi.python.org/pypi/graphene-elastic
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/graphene-elastic.svg
    :target: https://pypi.python.org/pypi/graphene-elastic/
    :alt: Supported Python versions

.. image:: https://travis-ci.org/barseghyanartur/graphene-elastic.svg?branch=master
    :target: https://travis-ci.org/barseghyanartur/graphene-elastic
    :alt: Build Status

.. image:: https://readthedocs.org/projects/graphene-elastic/badge/?version=latest
    :target: http://graphene-elastic.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-GPL--2.0--only%20OR%20LGPL--2.1--or--later-blue.svg
   :target: https://github.com/barseghyanartur/graphene-elastic/#License
   :alt: GPL-2.0-only OR LGPL-2.1-or-later

.. image:: https://coveralls.io/repos/github/barseghyanartur/graphene-elastic/badge.svg?branch=master
    :target: https://coveralls.io/github/barseghyanartur/graphene-elastic?branch=master
    :alt: Coverage

.. note::

    Project status is alpha.

Prerequisites
=============
- Graphene 2.x. *Support for Graphene 1.x is not intended.*
- Python 3.6, 3.7, 3.8. *Support for Python 2 is not intended.*
- Elasticsearch 6.x, 7.x. *Support for Elasticsearch 5.x is not intended.*

Main features and highlights
============================
- Implemented ``ElasticsearchConnectionField`` and ``ElasticsearchObjectType``
  are the core classes to work with ``graphene``.
- Pluggable backends for searching, filtering, ordering, etc. Don't like
  existing ones? Override, extend or write your own.
- Search backend.
- Filter backend.
- Ordering backend.
- Pagination.
- Highlighting backend.
- Source filter backend.
- Faceted search backend (including global aggregations).
- Post filter backend.
- Score filter backend.
- Query string backend.
- Simple query string backend.

See the `Road-map`_ for what's yet planned to implemented.

Do you need a similar tool for Django REST Framework? Check
`django-elasticsearch-dsl-drf
<https://github.com/barseghyanartur/django-elasticsearch-dsl-drf>`__.

Documentation
=============
Documentation is available on `Read the Docs
<http://graphene-elastic.readthedocs.io/>`_.

Installation
============
Install latest stable version from PyPI:

.. code-block:: bash

    pip install graphene-elastic

Or latest development version from GitHub:

.. code-block:: bash

    pip install https://github.com/barseghyanartur/graphene-elastic/archive/master.zip

Examples
========
Install requirements
--------------------
.. code-block:: sh

    pip install -r requirements.txt

Populate sample data
--------------------
The following command will create indexes for ``User`` and ``Post`` documents
and populate them with sample data:

.. code-block:: sh

    ./scripts/populate_elasticsearch_data.sh

Sample document definition
--------------------------
*search_index/documents/post.py*

See `examples/search_index/documents/post.py
<https://github.com/barseghyanartur/graphene-elastic/blob/master/examples/search_index/documents/post.py>`_
for full example.

.. code-block:: python

    import datetime
    from elasticsearch_dsl import (
        Boolean,
        Date,
        Document,
        InnerDoc,
        Keyword,
        Nested,
        Text,
        Integer,
    )

    class Comment(InnerDoc):

        author = Text(fields={'raw': Keyword()})
        content = Text(analyzer='snowball')
        created_at = Date()

        def age(self):
            return datetime.datetime.now() - self.created_at


    class Post(Document):

        title = Text(
            fields={'raw': Keyword()}
        )
        content = Text()
        created_at = Date()
        published = Boolean()
        category = Text(
            fields={'raw': Keyword()}
        )
        comments = Nested(Comment)
        tags = Text(
            analyzer=html_strip,
            fields={'raw': Keyword(multi=True)},
            multi=True
        )
        num_views = Integer()

        class Index:
            name = 'blog_post'
            settings = {
                'number_of_shards': 1,
                'number_of_replicas': 1,
                'blocks': {'read_only_allow_delete': None},
            }

Sample apps
-----------
Sample Flask app
~~~~~~~~~~~~~~~~
**Run the sample Flask app:**

.. code-block:: sh

    ./scripts/run_flask.sh

**Open Flask graphiql client**

.. code-block:: text

    http://127.0.0.1:8001/graphql

Sample Django app
~~~~~~~~~~~~~~~~~
**Run the sample Django app:**

.. code-block:: sh

    ./scripts/run_django.sh runserver

**Open Django graphiql client**

.. code-block:: text

    http://127.0.0.1:8000/graphql

ConnectionField example
~~~~~~~~~~~~~~~~~~~~~~~
ConnectionField is the most flexible and feature rich solution you have. It
uses filter backends which you can tie to your needs the way you want in a
declarative manner.

**Sample schema definition**

.. code-block:: python

    import graphene
    from graphene_elastic import (
        ElasticsearchObjectType,
        ElasticsearchConnectionField,
    )
    from graphene_elastic.filter_backends import (
        FilteringFilterBackend,
        SearchFilterBackend,
        HighlightFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
    )
    from graphene_elastic.constants import (
        LOOKUP_FILTER_PREFIX,
        LOOKUP_FILTER_TERM,
        LOOKUP_FILTER_TERMS,
        LOOKUP_FILTER_WILDCARD,
        LOOKUP_QUERY_EXCLUDE,
        LOOKUP_QUERY_IN,
    )

    # Object type definition
    class Post(ElasticsearchObjectType):

        class Meta(object):
            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                FilteringFilterBackend,
                SearchFilterBackend,
                HighlightFilterBackend,
                OrderingFilterBackend,
                DefaultOrderingFilterBackend,
            ]

            # For `FilteringFilterBackend` backend
            filter_fields = {
                # The dictionary key (in this case `title`) is the name of
                # the corresponding GraphQL query argument. The dictionary
                # value could be simple or complex structure (in this case
                # complex). The `field` key points to the `title.raw`, which
                # is the field name in the Elasticsearch document
                # (`PostDocument`). Since `lookups` key is provided, number
                # of lookups is limited to the given set, while term is the
                # default lookup (as specified in `default_lookup`).
                'title': {
                    'field': 'title.raw',
                    # Available lookups
                    'lookups': [
                        LOOKUP_FILTER_TERM,
                        LOOKUP_FILTER_TERMS,
                        LOOKUP_FILTER_PREFIX,
                        LOOKUP_FILTER_WILDCARD,
                        LOOKUP_QUERY_IN,
                        LOOKUP_QUERY_EXCLUDE,
                    ],
                    # Default lookup
                    'default_lookup': LOOKUP_FILTER_TERM,
                },

                # The dictionary key (in this case `category`) is the name of
                # the corresponding GraphQL query argument. Since no lookups
                # or default_lookup is provided, defaults are used (all lookups
                # available, term is the default lookup). The dictionary value
                # (in this case `category.raw`) is the field name in the
                # Elasticsearch document (`PostDocument`).
                'category': 'category.raw',

                # The dictionary key (in this case `tags`) is the name of
                # the corresponding GraphQL query argument. Since no lookups
                # or default_lookup is provided, defaults are used (all lookups
                # available, term is the default lookup). The dictionary value
                # (in this case `tags.raw`) is the field name in the
                # Elasticsearch document (`PostDocument`).
                'tags': 'tags.raw',

                # The dictionary key (in this case `num_views`) is the name of
                # the corresponding GraphQL query argument. Since no lookups
                # or default_lookup is provided, defaults are used (all lookups
                # available, term is the default lookup). The dictionary value
                # (in this case `num_views`) is the field name in the
                # Elasticsearch document (`PostDocument`).
                'num_views': 'num_views',
            }

            # For `SearchFilterBackend` backend
            search_fields = {
                'title': {'boost': 4},
                'content': {'boost': 2},
                'category': None,
            }

            # For `OrderingFilterBackend` backend
            ordering_fields = {
                # The dictionary key (in this case `tags`) is the name of
                # the corresponding GraphQL query argument. The dictionary
                # value (in this case `tags.raw`) is the field name in the
                # Elasticsearch document (`PostDocument`).
                'title': 'title.raw',

                # The dictionary key (in this case `created_at`) is the name of
                # the corresponding GraphQL query argument. The dictionary
                # value (in this case `created_at`) is the field name in the
                # Elasticsearch document (`PostDocument`).
                'created_at': 'created_at',

                # The dictionary key (in this case `num_views`) is the name of
                # the corresponding GraphQL query argument. The dictionary
                # value (in this case `num_views`) is the field name in the
                # Elasticsearch document (`PostDocument`).
                'num_views': 'num_views',
            }

            # For `DefaultOrderingFilterBackend` backend
            ordering_defaults = (
                '-num_views',  # Field name in the Elasticsearch document
                'title.raw',  # Field name in the Elasticsearch document
            )

            # For `HighlightFilterBackend` backend
            highlight_fields = {
                'title': {
                    'enabled': True,
                    'options': {
                        'pre_tags': ["<b>"],
                        'post_tags': ["</b>"],
                    }
                },
                'content': {
                    'options': {
                        'fragment_size': 50,
                        'number_of_fragments': 3
                    }
                },
                'category': {},
            }

    # Query definition
    class Query(graphene.ObjectType):
        all_post_documents = ElasticsearchConnectionField(Post)

    # Schema definition
    schema = graphene.Schema(query=Query)

Filter
^^^^^^

Sample queries
++++++++++++++

Since we didn't specify any lookups on `category`, by default all lookups
are available and the default lookup would be ``term``. Note, that in the
``{value:"Elastic"}`` part, the ``value`` stands for default lookup, whatever
it has been set to.

.. code-block:: javascript

    query PostsQuery {
      allPostDocuments(filter:{category:{value:"Elastic"}}) {
        edges {
          node {
            id
            title
            category
            content
            createdAt
            comments
          }
        }
      }
    }

But, we could use another lookup (in example below - ``terms``). Note, that
in the ``{terms:["Elastic", "Python"]}`` part, the ``terms`` is the lookup
name.

.. code-block:: javascript

    query PostsQuery {
      allPostDocuments(
            filter:{category:{terms:["Elastic", "Python"]}}
        ) {
        edges {
          node {
            id
            title
            category
            content
            createdAt
            comments
          }
        }
      }
    }

Or apply a ``gt`` (``range``) query in addition to filtering:

.. code-block:: javascript

    {
      allPostDocuments(filter:{
            category:{term:"Python"},
            numViews:{gt:"700"}
        }) {
        edges {
          node {
            category
            title
            comments
            numViews
          }
        }
      }
    }

Implemented filter lookups
++++++++++++++++++++++++++
The following lookups are available:

- ``contains``
- ``ends_with`` (or ``endsWith`` for camelCase)
- ``exclude``
- ``exists``
- ``gt``
- ``gte``
- ``in``
- ``is_null`` (or ``isNull`` for camelCase)
- ``lt``
- ``lte``
- ``prefix``
- ``range``
- ``starts_with`` (or ``startsWith`` for camelCase)
- ``term``
- ``terms``
- ``wildcard``

See `dedicated documentation on filter lookups
<https://graphene-elastic.readthedocs.io/en/latest/filtering.html>`__ for
more information.

Search
^^^^^^
Search in all fields:

.. code-block:: javascript

    query {
      allPostDocuments(
        search:{query:"Release Box"}
      ) {
        edges {
          node {
            category
            title
            content
          }
        }
      }
    }

Search in specific fields:

.. code-block:: javascript

    query {
      allPostDocuments(
        search:{
            title:{value:"Release", boost:2},
            content:{value:"Box"}
        }
      ) {
        edges {
          node {
            category
            title
            content
          }
        }
      }
    }

Ordering
^^^^^^^^
Possible choices are ``ASC`` and ``DESC``.

.. code-block:: javascript

    query {
      allPostDocuments(
            filter:{category:{term:"Photography"}},
            ordering:{title:ASC}
        ) {
        edges {
          node {
            category
            title
            content
            numViews
            tags
          }
        }
      }
    }

Pagination
^^^^^^^^^^
The ``first``, ``last``, ``before`` and ``after`` arguments are supported.
By default number of results is limited to 100.

.. code-block:: javascript

    query {
      allPostDocuments(first:12) {
        pageInfo {
          startCursor
          endCursor
          hasNextPage
          hasPreviousPage
        }
        edges {
          cursor
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Highlighting
^^^^^^^^^^^^
Simply, list the fields you want to highlight. This works only in combination
with search.

.. code-block:: javascript

    query {
      allPostDocuments(
            search:{content:{value:"alice"}, title:{value:"alice"}},
            highlight:[category, content]
        ) {
        edges {
          node {
            title
            content
            highlight
          }
          cursor
        }
      }
    }

Road-map
========
Road-map and development plans.

This package was designed after `django-elasticsearch-dsl-drf
<https://github.com/barseghyanartur/django-elasticsearch-dsl-drf>`__.
It's intended to offer similar functionality in ``graphene-elastic`` (this
package).

Lots of features are planned to be released in the upcoming Beta releases:

- Suggester backend.
- Nested backend.
- Geo-spatial backend.
- Filter lookup ``geo_bounding_box`` (or ``geoBoundingBox`` for camelCase).
- Filter lookup ``geo_distance`` (or ``geoDistance`` for camelCase).
- Filter lookup ``geo_polygon`` (or ``geoPolygon`` for camelCase).
- More-like-this backend.

Stay tuned or reach out if you want to help.

Testing
=======
Project is covered with tests.

Running tests
-------------
By defaults tests are executed against the Elasticsearch 7.x.

**Run Elasticsearch 7.x with Docker**

.. code-block:: bash

    docker-compose up elasticsearch

**Install test requirements**

.. code-block:: sh

    pip install -r requirements/test.txt

To test with all supported Python versions type:

.. code-block:: sh

    tox

To test against specific environment, type:

.. code-block:: sh

    tox -e py38-elastic7

To test just your working environment type:

.. code-block:: sh

    ./runtests.py

To run a single test module in your working environment type:

.. code-block:: sh

    ./runtests.py src/graphene_elastic/tests/test_filter_backend.py

To run a single test class in a given test module in your working environment
type:

.. code-block:: sh

    ./runtests.py src/graphene_elastic/tests/test_filter_backend.py::FilterBackendElasticTestCase

Testing with Docker
-------------------
.. code-block:: sh

    docker-compose -f docker-compose.yml -f docker-compose-test.yml up --build test

Debugging
=========
For development purposes, you could use the flask app (easy to debug). Standard
``pdb`` works (``import pdb; pdb.set_trace()``). If ``ipdb`` does not work
well for you, use ``ptpdb``.

Writing documentation
=====================
Keep the following hierarchy.

.. code-block:: text

    =====
    title
    =====

    header
    ======

    sub-header
    ----------

    sub-sub-header
    ~~~~~~~~~~~~~~

    sub-sub-sub-header
    ^^^^^^^^^^^^^^^^^^

    sub-sub-sub-sub-header
    ++++++++++++++++++++++

    sub-sub-sub-sub-sub-header
    **************************

License
=======
GPL-2.0-only OR LGPL-2.1-or-later

Support
=======
For any issues contact me at the e-mail given in the `Author`_ section.

Author
======
Artur Barseghyan <artur.barseghyan@gmail.com>
