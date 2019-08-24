from graphene.test import Client

from graphql_schema.schema import schema


def posts():
    client = Client(schema)
    query = ''' 
        query { 
            posts { 
                title 
                category
                comments {
                    author
                }
            } 
        } 
    '''
    executed = client.execute(query)
    assert executed == {
        'data': {
            'hey': 'hello!'
        }
    }
