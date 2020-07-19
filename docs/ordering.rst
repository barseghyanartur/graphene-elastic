Ordering
========
Possible choices are ``ASC`` and ``DESC``.

.. code-block:: javascript

    query {
      allPostDocuments(
            filter:{category:{term:"Photography"}},
            ordering:{title:ASC}
        ) {
        edges {
          node {
            category
            title
            content
            numViews
            tags
          }
        }
      }
    }

Multiple values are allowed:

.. code-block:: javascript

    query {
      allPostDocuments(
            filter:{category:{term:"Photography"}},
            ordering:{numViews:DESC, createdAt:ASC}
        ) {
        edges {
          node {
            category
            title
            content
            numViews
            tags
          }
        }
      }
    }

Ordering by score is implemented as well:

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
