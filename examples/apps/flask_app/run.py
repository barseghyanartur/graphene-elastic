from flask import Flask
from flask_graphql import GraphQLView

from inject import *  # Should be present before any other project imports
from schema import schema

app = Flask(__name__)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

# Optional, for adding batch query support (used in Apollo-Client)
# app.add_url_rule(
#     '/graphql/batch',
#     view_func=GraphQLView.as_view('graphql', schema=schema, batch=True)
# )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8001')
