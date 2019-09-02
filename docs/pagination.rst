Pagination
==========
Limits
------
By default, max number of fetched items is limited to 100. It's configurable.
Set the ``RELAY_CONNECTION_MAX_LIMIT`` setting to the desired value.

Enforce ``first`` or ``last``
-----------------------------
You could force users to provide ``first`` or ``last``. Set
``RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST`` to ``True`` for that.

User controlled pagination
--------------------------
The following (standard) arguments are available:

- first
- last
- before
- after

Sample query to return all results (limited by
``RELAY_CONNECTION_MAX_LIMIT`` setting only):

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

Sample query to return first 12 results:

.. code-block:: javascript

    {
      allPostDocuments(first:12) {
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

Sample query to return first 12 results after the given offset:

.. code-block:: javascript
    {
      allPostDocuments(first:12, after:"YXJyYXljb25uZWN0aW9uOjEx") {
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
