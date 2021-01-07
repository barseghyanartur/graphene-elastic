See the updated example project (the very minimal configuration to have 
authentication checks working):

- [Example schema definition](https://github.com/barseghyanartur/graphene-elastic/blob/master/examples/schema/post/connection.py#L13)
- [Updated connection field](https://github.com/barseghyanartur/graphene-elastic/blob/master/examples/schema/post/connection.py#L77)
- [Django admin routes](https://github.com/barseghyanartur/graphene-elastic/blob/master/examples/apps/django_app/run.py#L51)

1. Create a Django user

```./scripts/run_django.sh createsuperuser```

2. Run Elasticsearch

```docker-compose up```

3. Add some data to the Elasticsearch

```./scripts/populate_elasticsearch_data.sh```

4. Run the example project:

```./scripts/run_django.sh runserver```

5. Go to http://localhost:8000/admin/ and enter your credentials

6. Go to http://localhost:8000/graphql and type in the following query:

```graphql
query PostsQuery {
      postDocumentsForUser {
        edges {
          node {
            id
            title
            userId
          }
        }
      }
    }
```
