from django.core.management.base import BaseCommand, CommandError
from factories.generate import generate


class Command(BaseCommand):
    help = 'Generate'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        # for poll_id in options['poll_ids']:
        generate()
        self.stdout.write(self.style.SUCCESS('Successfully generated'))
