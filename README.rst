================
graphene-elastic
================
`Elasticsearch (DSL) <https://elasticsearch-dsl.readthedocs.io/en/latest/>`__
integration for `Graphene <http://graphene-python.org/>`__.

.. image:: https://travis-ci.org/barseghyanartur/graphene-elastic.svg?branch=master
    :target: https://travis-ci.org/barseghyanartur/graphene-elastic
.. image:: https://coveralls.io/repos/github/barseghyanartur/graphene-mongo/badge.svg?branch=master
    :target: https://coveralls.io/github/barseghyanartur/graphene-elastic?branch=master
.. image:: https://badge.fury.io/py/graphene-elastic.svg
    :target: https://badge.fury.io/py/graphene-elastic
.. image:: https://img.shields.io/pypi/pyversions/graphene-elastic.svg
    :target: https://pypi.python.org/pypi/graphene-elastic/

.. note::

    Project status is alpha.

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
*documents.py*

.. code-block:: python

    from elasticsearch_dsl import Document, Text

    class User(Document):
        first_name = Text()
        last_name = Text()
        email = Text()
        created_at = Date()

        class Index:
            name = 'site_user'
            settings = {
                'number_of_shards': 1,
                'number_of_replicas': 1,
                'blocks': {'read_only_allow_delete': None},
            }

        def save(self, ** kwargs):
            self.created_at = datetime.datetime.now()
            return super().save(** kwargs)


    try:
        # Create the mappings in Elasticsearch
        User.init()
    except Exception as err:
        logger.error(err)


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

Stay tuned.

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
