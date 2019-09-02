Quick start
===========
Clone the repository
--------------------
.. code-block:: sh

    git clone git@github.com:barseghyanartur/graphene-elastic.git && graphene-elastic

Start Elasticsearch
-------------------
.. code-block:: sh

    docker-compose up elasticsearch

Install requirements
--------------------
.. code-block:: sh

    pip install -r requirements.txt

Populate dummy data
-------------------
.. code-block:: sh

    ./scripts/populate_elasticsearch_data.sh

Open the browser
----------------
http://127.0.0.1:8000/graphql

Make some experiments
---------------------
.. code-block:: javascript

    {
      allPostDocuments {
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

Run tests
---------
.. code-block:: sh

    ./runtests.py
