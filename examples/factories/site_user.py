from factory import Faker
# from factory.base import Factory

from search_index.documents import User

from .elasticsearch_dsl_factory import ElasticsearchFactory

__all__ = (
    'UserFactory',
)


class UserFactory(ElasticsearchFactory):
    """User factory."""

    class Meta(object):
        model = User

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    created_at = Faker('date')
    email = Faker('email')
    is_active = Faker('pybool')
