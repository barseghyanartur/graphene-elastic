import os
import sys
import uuid

from faker import Faker


def project_dir(base):
    """Absolute path to a file from current directory."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), base).replace('\\', '/')
    )


sys.path.insert(0, project_dir("../../examples"))

from factories.blog_post import PostFactory
from factories.site_user import UserFactory
from factories.farm_animal import AnimalFactory


def generate(num_items=100):
    """Generate data.

    :param num_items: Number of items to generate.
    :type num_items: int
    :return:
    """
    # Generic Post data
    posts = PostFactory.create_batch(num_items)

    for post in posts:
        post.save()

    # Specific Post data
    faker = Faker()
    post = PostFactory(title="Alice", )
    white_rabbit = "White Rabbit is dead {}".format(
        uuid.uuid4()
    )
    post.content = "{} {} {}".format(
        faker.paragraph(),
        white_rabbit,
        faker.paragraph(),
    )
    post.save()

    # Generic User data
    users = UserFactory.create_batch(num_items)

    for user in users:
        user.save()

    # Generic Animal data
    animals = AnimalFactory.create_batch(num_items)

    for animal in animals:
        animal.save()


if __name__ == '__main__':
    generate()
