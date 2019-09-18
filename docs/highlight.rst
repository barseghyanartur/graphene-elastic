Highlight
=========
**Sample type definition:**

.. code-block:: python

    from graphene import Node
    from graphene_elastic import ElasticsearchObjectType
    from graphene_elastic.filter_backends import HighlightFilterBackend

    class Post(ElasticsearchObjectType):

        class Meta:

            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                # ...
                HighlightFilterBackend,  # Important
                # ...
            ]

            # ...

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

            # ...

**Sample query:**

.. code-block:: javascript

    query {
      allPostDocuments(
            search:{content:{value:"since"}, title:{value:"decide"}},
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

**Sample response:**

.. code-block:: javascript

    {
      "data": {
        "allPostDocuments": {
          "edges": [
            {
              "node": {
                "title": "PM decide.",
                "content": "Cut dog young only. Whole natural state Republican year.\nFinancial oil current sea. Mind large similar probably lawyer since. Son control fire remember.",
                "highlight": {
                  "title": [
                    "PM <b>decide</b>."
                  ],
                  "content": [
                    "Mind large similar probably lawyer <em>since</em>."
                  ]
                }
              },
              "cursor": "YXJyYXljb25uZWN0aW9uOjA="
            },
            {
              "node": {
                "title": "Many add.",
                "content": "Read almost consumer perform water. Really protect push send body wind. Training point since involve public last let new.",
                "highlight": {
                  "content": [
                    "Training point <em>since</em> involve public last let new."
                  ]
                }
              },
              "cursor": "YXJyYXljb25uZWN0aW9uOjE="
            }
        }
      }
    }
