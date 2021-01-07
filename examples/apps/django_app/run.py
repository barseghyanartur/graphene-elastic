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
    "MIDDLEWARE": (
        "graphene_django.debug.DjangoDebugMiddleware",
    ),
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

configure(locals(), django_admin=True)

# ************************************************************************
# ********************* graphene-elastic routes **************************
# ************************************************************************
from graphene_django.views import GraphQLView  # NOQA
from graphene_elastic.settings import graphene_settings  # NOQA
route(
    'graphql',
    GraphQLView.as_view(
        graphiql=True,
        middleware=graphene_settings.MIDDLEWARE
    ),
)

# ************************************************************************
# **************************** django routes *****************************
# ************************************************************************
from django.contrib import admin
route('admin/', admin.site.urls),

if __name__ == '__main__':
    application = run()
