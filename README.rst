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
  existing ones? Extend or write your own.
- Implemented search backend.
- Implemented filter backend.

See the `Road-map`_ for what's yet planned to implemented.

Documentation
=============
Documentation is available on `Read the Docs
<http://graphene-elastic.readthedocs.io/>`_.

Installation
============
For installing ``graphene-elastic``, just run this command in your shell:

.. code-block:: bash

    pip install graphene-elastic

Examples
========
Install requirements
--------------------
.. code-block:: sh

    pip install -r examples/requirements.txt

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
<https://github.com/barseghyanartur/graphene-elastic/examples/search_index/documents/post.py>`_
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

        class Index:
            name = 'blog_post'
            settings = {
                'number_of_shards': 1,
                'number_of_replicas': 1,
                'blocks': {'read_only_allow_delete': None},
            }

        def add_comment(self, author, content):
            self.comments.append(
                Comment(
                    author=author,
                    content=content,
                    created_at=datetime.datetime.now()
                )
            )

        def save(self, ** kwargs):
            self.created_at = datetime.datetime.now()
            return super().save(** kwargs)

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
ConnectionField is more flexible. It uses filter backends which you can tie
to your needs the way you want in a declarative way.

.. code-block:: python

    import graphene
    from graphene_elastic import (
        ElasticsearchObjectType,
        ElasticsearchConnectionField,
    )
    from graphene_elastic.filter_backends import (
        FilteringFilterBackend,
        SearchFilterBackend,
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
            ]
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
            }
            search_fields = {
                'title': {'boost': 4},
                'content': {'boost': 2},
                'category': None,
            }


    # Query definition
    class Query(graphene.ObjectType):
        all_post_documents = ElasticsearchConnectionField(Post)

    # Schema definition
    schema = graphene.Schema(query=Query)

**Filter**

Since we didn't specify any lookups on `category`, by default all lookups
are available. Default lookup would be `LOOKUP_FILTER_TERM`.

.. code-block:: javascript

    query PostsQuery {
      allPostDocuments(filter:{category:{query:["Elastic"]}}) {
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

But, we could use another lookup by adding it to the query:

.. code-block:: javascript

    query PostsQuery {
      allPostDocuments(filter:{category:{query:["tic"], lookup:ENDSWITH}}) {
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

**Search**

.. code-block:: javascript

    query {
      allPostDocuments(
        search:{title:{query:"Release", boost:1}, content:{query:"Box"}}}
      ) {
        edges {
          node {
            category
            title
            comments
          }
        }
      }
    }

Road-map
========
Road-map and development plans.

Lots of features are planned to be released in the upcoming Beta releases:

- Ordering backend
- Geo-spatial backend
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

To test with all supported Python versions type:

.. code-block:: sh

    tox

To test against specific environment, type:

.. code-block:: sh

    tox -e py37

To test just your working environment type:

.. code-block:: sh

    ./runtests.py

.. code-block:: sh

    pip install -r examples/requirements/test.txt

Debugging
=========
For development purposes, you could use the flask app (easy to debug). Standard
``pdb`` works (``import pdb; pdb.set_trace()``). If ``ipdb`` does not work
well for you, use ``ptpdb`` does.

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
