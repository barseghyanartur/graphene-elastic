from fastapi import FastAPI
from starlette.graphql import GraphQLApp

from inject import *  # Should be present before any other project imports

try:
    from local_overrides import *
except ImportError as err:
    print(err)

from schema import schema

app = FastAPI()
app.add_route("/", GraphQLApp(schema=schema, graphiql=True))
