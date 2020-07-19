Score
=====
Score is [relevance](https://www.elastic.co/guide/en/elasticsearch/reference/7.x/query-filter-context.html)
in Elasticsearch.

**Sample type definition:**

.. code-block:: python

    from graphene import Node
    from graphene_elastic import ElasticsearchObjectType
    from graphene_elastic.filter_backends import ScoreFilterBackend, OrderingFilterBackend

    class Post(ElasticsearchObjectType):

        class Meta:

            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                # ...
                ScoreFilterBackend,  # Important
                OrderingFilterBackend,  # Important
                # ...
            ]


            # For `OrderingFilterBackend` backend
            ordering_fields = {
                # Score
                'score': '_score',
            }

**Sample query:**

Note, that we want to order by relevance (most relevant on top).

.. code-block:: javascript

    query {
      allPostDocuments(
            search:{query:"Alice"},
            ordering:{score:DESC}
        ) {
        edges {
          node {
            id
            title
            content
            category
            createdAt
            score
          }
        }
      }
    }

**Sample response:**

As you could see, score is calculated.

.. code-block:: javascript

    {
      "data": {
        "allPostDocuments": {
          "edges": [
            {
              "node": {
                "id": "UG9zdDpMNnBiV1hNQjhYRzdJclZ2X20waA==",
                "title": "Budget.",
                "category": "Elastic",
                "content": "Bed television public teacher behind human up.\nMind anyone politics ball cost wife try adult. College work for.\nPlay five ten not sort energy.\nCommon word behind spring. All behind voice policy.",
                "createdAt": "1973-03-12T00:00:00",
                "score": 20.420774
              }
            },
            ...
           ]
        }
      }
    }
