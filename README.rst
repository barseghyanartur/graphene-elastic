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
- Graphene 2.x. *Support for Graphene 1.x is not planned, but might be considered.*
- Python 3.6, 3.7. *Support for Python 2 is not intended.*
- Elasticsearch 6.x, 7.x. *Support for Elasticsearch 5.x is not intended.*

Main features and highlights
============================
- Implemented ``ElasticsearchConnectionField`` and ``ElasticsearchObjectType``
  are the core classes to work with ``graphene``.
- Pluggable backends for searching, filtering, ordering, etc. Don't like
  existing ones? Override, extend or write your own.
- Implemented search backend.
- Implemented filter backend.
- Implemented ordering backend.
- Implemented pagination.

See the `Road-map`_ for what's yet planned to implemented.

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

**Open Flask graphiql client**

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
                OrderingFilterBackend,
                DefaultOrderingFilterBackend,
            ]

            # For `FilteringFilterBackend` backend
            filter_fields = {
                'title': {
                    'field': 'title.raw',
                    'lookups': [
                        LOOKUP_FILTER_TERM,
                        LOOKUP_FILTER_TERMS,
                        LOOKUP_FILTER_PREFIX,
                        LOOKUP_FILTER_WILDCARD,
                        LOOKUP_QUERY_IN,
                        LOOKUP_QUERY_EXCLUDE,
                    ],
                    'default_lookup': LOOKUP_FILTER_TERM,
                },
                'category': 'category.raw',
                'tags': 'tags.raw',
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
                'title': 'title.raw',
                'created_at': 'created_at',
                'num_views': 'num_views',
            }

            # For `DefaultOrderingFilterBackend` backend
            ordering_defaults = (
                '-num_views',
                'title.raw',
            )

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
      allPostDocuments(filter:{
            category:{terms:["Elastic", "Python"]}
        }) {
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
<https://graphene-elastic.readthedocs.io/en/latest/filter_lookups.html>`__ for
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
      allPostDocuments(filter:{
            tags:{in:["photography", "models"]},
            ordering:{title:ASC}
        }) {
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

Road-map
========
Road-map and development plans.

Lots of features are planned to be released in the upcoming Beta releases:

- Geo-spatial backend
- Filter lookup ``geo_bounding_box`` (or ``geoBoundingBox`` for camelCase)
- Filter lookup ``geo_distance`` (or ``geoDistance`` for camelCase)
- Filter lookup ``geo_polygon`` (or ``geoPolygon`` for camelCase)
- Aggregations (faceted search) backend
- Post-filter backend
- Nested backend
- Highlight backend
- Suggester backend
- Global aggregations backend
- More-like-this backend
- Complex search backends, such as Simple query search
- Source filter backend

Stay tuned or reach out if you want to help.

Testing
=======
Project is covered with tests.

By defaults tests are executed against the Elasticsearch 7.x.

Running Elasticsearch
---------------------
**Run Elasticsearch 7.x with Docker**

.. code-block:: bash

    docker-compose up elasticsearch

Running tests
-------------
Make sure you have the test requirements installed:

.. code-block:: sh

    pip install -r requirements/test.txt

To test with all supported Python versions type:

.. code-block:: sh

    tox

To test against specific environment, type:

.. code-block:: sh

    tox -e py37

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
