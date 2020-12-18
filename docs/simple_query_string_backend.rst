Simple query string backend
===========================
Implementation of
`Simple query string query <https://www.elastic.co/guide/en/elasticsearch/reference/7.x/query-dsl-simple-query-string-query.html>`__.

**Sample type definition**

.. code-block:: python

    from graphene import Node
    from graphene_elastic import ElasticsearchObjectType
    from graphene_elastic.filter_backends import SimpleQueryStringBackend

    class Post(ElasticsearchObjectType):

        class Meta:

            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                # ...
                SimpleQueryStringBackend,  # Important
                # ...
            ]

            simple_query_string_options = {
                "fields": ["title^2", "content", "category"],
                "boost": 2,
            }

**Sample query**

.. code-block:: graphql

    query PostsQuery {
      allPostDocuments(
        simpleQueryString:"'White Rabbit' +Alice"
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
