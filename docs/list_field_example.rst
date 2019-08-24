List field example
~~~~~~~~~~~~~~~~~~
Sample GraphQL schema definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*schema.py*

.. code-block:: python

    import graphene

    from graphene_elastic import ElasticsearchObjectType

    from .documents import User as UserDocument

    # User object type
    class User(ElasticsearchObjectType):
        class Meta:
            document = UserDocument

    # Graphene query
    class Query(graphene.ObjectType):
        users = graphene.List(User)

        def resolve_users(self, info):
            return UserDocument.search().scan()

    # Schema
    schema = graphene.Schema(query=Query, auto_camelcase=False)

Querying
^^^^^^^^
Sample query:

.. code-block:: python

    query = """
        query {
            users {
                first_name
                last_name
                email
                created_at
            }
        }
    """
    result = schema.execute(query)

To learn more check out the `Flask Elasticsearch example app
<https://github.com/barseghyanartur/graphene-elastic/tree/master/examples/flask_app>`__

**Run sample query**

.. code-block:: javascript

    {
      posts {
        title
        content
        category
        created_at
        comments
      }
      users {
        first_name
        last_name
        email
        created_at
      }
    }

**Sample results**

.. code-block:: javascript

    {
      "data": {
        "posts": [
          {
            "title": "Thus.",
            "content": "Yourself need nation bit language. Defense seven series black become low attorney.",
            "category": "Elastic",
            "created_at": "2019-06-25T17:22:16.573003",
            "comments": [
              {
                "author": "Dr. Christy Watson",
                "content": "Low article resource anyone which million. Sit forward hospital long window wide.",
                "created_at": "1990-07-03T00:00:00"
              }
            ]
          },
          {
            "title": "Change.",
            "content": "Development system bed condition same. Argue just field bank best girl player.",
            "category": "Model Photography",
            "created_at": "2019-06-25T17:22:16.672518",
            "comments": [
              {
                "author": "Jason Berry",
                "content": "Body tax TV nature return national market land. Society common billion like.",
                "created_at": "1990-01-12T00:00:00"
              }
            ]
          }
        ],
        "users": [
          {
            "first_name": "Tiffany",
            "last_name": "Garrett",
            "email": "timothy89@raymond-lee.com",
            "created_at": "2019-06-25T17:22:18.352804"
          },
          {
            "first_name": "Jenna",
            "last_name": "Mcconnell",
            "email": "eddie19@hotmail.com",
            "created_at": "2019-06-25T17:22:18.367279"
          }
        ]
      }
    }
