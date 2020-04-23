Source
======
Source query is meant to lighten the Elasticsearch load by reducing amount
of data sent around. Although GraphQL seems to have solved the issue between
frontend and backend, Elasticsearch would still send all the data to the
backend. That's where we might use the source backend.

**Sample type definition:**

.. code-block:: python

    from graphene import Node
    from graphene_elastic import ElasticsearchObjectType
    from graphene_elastic.filter_backends import SourceFilterBackend

    class Post(ElasticsearchObjectType):

        class Meta:

            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                # ...
                SourceFilterBackend,  # Important
                # ...
            ]


**Sample query:**

.. code-block:: javascript

    query {
      allPostDocuments(
            search:{content:{value:"alice"}, title:{value:"alice"}},
            source:[title, id]
        ) {
        edges {
          node {
            id
            title
            content
            category
            comments
          }
          cursor
        }
      }
    }

**Sample response:**

As you could see, although we do ask for more fields in the ``node {...}``
part, the requested fields are empty. We only get data in the fields we
have specified in ``source`` (they are ``title`` and ``id``).

.. code-block:: javascript

    {
      "data": {
        "allPostDocuments": {
          "edges": [
            {
              "node": {
                "id": "UG9zdDpvX0huUlcwQlhfYXJjd2RMc0w2aQ==",
                "title": "only Alice miss",
                "content": null,
                "category": null,
                "comments": []
              },
              "cursor": "YXJyYXljb25uZWN0aW9uOjA="
            },
            {
              "node": {
                "id": "UG9zdDpvZkhuUlcwQlhfYXJjd2RMc0w1Nw==",
                "title": "prevent Alice citizen",
                "content": null,
                "category": null,
                "comments": []
              },
              "cursor": "YXJyYXljb25uZWN0aW9uOjE="
            }
          ]
        }
      }
    }
