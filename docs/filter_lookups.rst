Filter lookups
==============

The following lookups are available:

- ``contains``
- ``ends_with`` (or ``endsWith`` for camelCase)
- ``exclude``
- ``exists``
- ``gt``
- ``gte``
- ``in``
- ``is_null`` (or ``isNull`` for camelCase)
- ``lt``
- ``lte``
- ``prefix``
- ``range``
- ``starts_with`` (or ``startsWith`` for camelCase)
- ``term``
- ``terms``
- ``wildcard``

Filter lookup contains
----------------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{contains:"tho"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup ends_with
-----------------------
.. note::

    ``endsWith`` for camelCase.

.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{endsWith:"thon"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup exclude
---------------------
For a single term:

.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{exclude:"Python"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

For multiple terms:

.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{exclude:["Python", "Django"]}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }


Filter lookup exists
--------------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{exists:true}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup gt
----------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{numViews:{gt:"100"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup gte
-----------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{numViews:{gte:"100"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup in
----------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{tags:{in:["photography", "models"]}}) {
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

Filter lookup lt
----------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{numViews:{lt:"200"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup lte
-----------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{numViews:{lte:"200"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup prefix
--------------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{prefix:"Pyth"}}) {
        edges {
          node {
            category
            title
            content
            numViews
            comments
          }
        }
      }
    }

Filter lookup range
-------------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{numViews:{range:{
            lower:"100",
            upper:"200"
          }}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup starts_with
-------------------------
.. note::

    ``startsWith`` for camelCase.

Alias for `Filter lookup prefix`_.

Filter lookup term
------------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{term:"Python"}}) {
        edges {
          node {
            category
            title
            content
            numViews
            comments
          }
        }
      }
    }

Filter lookup terms
-------------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{terms:["Python", "Django"]}}) {
        edges {
          node {
            category
            title
            content
            numViews
            comments
          }
        }
      }
    }

Filter lookup wildcard
----------------------
.. code-block:: javascript

    query {
      allPostDocuments(filter:{category:{wildcard:"*ytho*"}}) {
        edges {
          node {
            category
            title
            content
            numViews
            comments
          }
        }
      }
    }
