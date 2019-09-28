Post-filter backend
===================
Works the same way as ``FilteringFilterBackend``, but does not affect
aggregations.

Filter lookups
--------------
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

Filter lookup ``contains``
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{contains:"tho"}}) {
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

Filter lookup ``ends_with``
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. note::

    ``endsWith`` for camelCase.

.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{endsWith:"thon"}}) {
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

Filter lookup ``exclude``
~~~~~~~~~~~~~~~~~~~~~~~~~
**For a single term:**

.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{exclude:"Python"}}) {
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

**For multiple terms:**

.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{exclude:["Python", "Django"]}}) {
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


Filter lookup ``exists``
~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{exists:true}}) {
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

Filter lookup ``gt``
~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{numViews:{gt:"100"}}) {
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

Filter lookup ``gte``
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{numViews:{gte:"100"}}) {
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

Filter lookup ``in``
~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{tags:{in:["photography", "models"]}}) {
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

Filter lookup ``lt``
~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{numViews:{lt:"200"}}) {
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

Filter lookup ``lte``
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{numViews:{lte:"200"}}) {
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

Filter lookup ``prefix``
~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{prefix:"Pyth"}}) {
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

Filter lookup ``range``
~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{numViews:{range:{
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

Filter lookup ``starts_with``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. note::

    ``startsWith`` for camelCase.

*Alias for filter lookup ``prefix``.*

Filter lookup ``term``
~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{term:"Python"}}) {
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

Filter lookup ``terms``
~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{terms:["Python", "Django"]}}) {
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

Filter lookup ``wildcard``
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{category:{wildcard:"*ytho*"}}) {
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
