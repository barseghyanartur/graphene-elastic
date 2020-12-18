Query string backend
====================
Implementation of
`Query string query <https://www.elastic.co/guide/en/elasticsearch/reference/7.x/query-dsl-query-string-query.html>`__.

**Sample type definition**

.. code-block:: python

    from graphene import Node
    from graphene_elastic import ElasticsearchObjectType
    from graphene_elastic.filter_backends import QueryStringBackend

    class Post(ElasticsearchObjectType):

        class Meta:

            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                # ...
                QueryStringBackend,  # Important
                # ...
            ]

            query_string_options = {
                "fields": ["title^2", "content", "category"],
                "boost": 2,
            }

**Sample query**

.. code-block:: graphql

    query PostsQuery {
      allPostDocuments(
        queryString:"(White Rabbit) AND Alice"
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

**Sample response**

.. code-block:: javascript

    {
      "data": {
        "allPostDocuments": {
          "edges": [
            {
              "node": {
                "id": "UG9zdDppLVozZDNZQmNDeUtjYnh5WTU5Vg==",
                "title": "Alice",
                "category": "MongoDB",
                "content": "Personal green well method day report. White Rabbit is dead. Take stuff newspaper soldier up.",
                "createdAt": "1994-01-01T00:00:00",
                "comments": [
                  {
                    "author": "Matthew Jones",
                    "content": "Despite consumer safe since range opportunity.",
                    "created_at": "1970-05-05T00:00:00"
                  },
                  {
                    "author": "Larry Brown",
                    "content": "Environment drug artist. Pattern source sound hope trip.",
                    "created_at": "2005-07-24T00:00:00"
                  }
                ]
              }
            }
          ]
        }
      }
    }
