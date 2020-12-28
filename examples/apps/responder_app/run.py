import responder

from inject import *  # Should be present before any other project imports

from schema import schema

api = responder.API()

view = responder.ext.GraphQLView(
    api=api,
    schema=schema
)

api.add_route("/graphql", view)

if __name__ == '__main__':
    api.run(debug=True, port=8001)
