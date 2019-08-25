import os

from django_micro import configure, route, run

from inject import *  # NOQA

try:
    from local_overrides import *
except ImportError as err:
    print(err)

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    "graphene_django",
    "schema",
]

GRAPHENE = {
    "SCHEMA": "schema.schema",
    "SCHEMA_INDENT": 2,
    "MIDDLEWARE": ("graphene_django.debug.DjangoDebugMiddleware",),
}


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

configure(locals(), django_admin=True)

from graphene_django.views import GraphQLView

route('graphql', GraphQLView.as_view(graphiql=True))

if __name__ == '__main__':
    application = run()
