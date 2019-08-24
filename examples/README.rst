**Install requirements**

.. code-block:: sh

    pip install -r examples/requirements.txt

**Run Elasticsearch**

Using docker:

.. code-block:: sh

    docker-compose-up elasticsearch

Or simply run the version you want (note that in this case your data is not
persistent and you will have to build index each time you start).

.. code-block:: sh

    ./scripts/elasticsearch_start.sh --version 7.1.1

**Populate Elasticsearch with data**

.. code-block:: sh

    ./scripts/populate_elasticsearch_data.sh

**Run REST API**

.. code-block:: sh

    ./scripts/run_flask.sh

**Open posts endpoint**

.. code-block:: text

    http://localhost:8001/graphql
