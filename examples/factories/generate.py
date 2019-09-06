import os
import sys


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
    posts = PostFactory.create_batch(num_items)

    for post in posts:
        post.save()

    users = UserFactory.create_batch(num_items)

    for user in users:
        user.save()

    animals = AnimalFactory.create_batch(num_items)

    for animal in animals:
        animal.save()


if __name__ == '__main__':
    generate()
