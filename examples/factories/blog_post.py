import random
import factory
from factory import Faker
from factory.base import Factory
from factory.fuzzy import FuzzyChoice

from search_index.documents import Post


__all__ = (
    'Comment',
    'CommentFactory',
    'PostFactory',
    'ManyViewsPostFactory',
)


class Comment(object):
    """Comment model (we need one for factories)."""

    def __init__(self, *args, **kwargs):
        self.author = kwargs.get('author')
        self.content = kwargs.get('content')
        self.created_at = kwargs.get('created_at')

    def items(self):
        return self.to_dict().items()

    def to_dict(self):
        return self.__dict__


class CommentFactory(Factory):
    """Comment factory."""

    author = Faker('name')
    content = Faker('text')
    created_at = Faker('date')

    class Meta(object):
        model = Comment


class PostFactory(Factory):
    """Post factory."""

    class Meta(object):
        model = Post

    title = Faker('text', max_nb_chars=10)
    content = Faker('text')
    created_at = Faker('date')
    published = FuzzyChoice([True, False])
    category = FuzzyChoice([
        'Elastic',
        'MongoDB',
        'Machine Learning',
        'Model Photography',
        'Python',
        'Django',
    ])
    num_views = Faker('pyint', min_value=0, max_value=1000)

    @factory.post_generation
    def comments(obj, create, extracted, **kwargs):
        if create:
            obj.comments = CommentFactory.create_batch(
                size=random.randint(1, 6)
            )


class ManyViewsPostFactory(PostFactory):
    num_views = Faker('pyint', min_value=2000, max_value=10000)
