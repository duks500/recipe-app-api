import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


# BaseCommand is the calss that we want to build on
class Command(BaseCommand):
    """Django command to pause execution util database is available"""

    # What function run after calling the command
    def handle(self, *args, **options):
        # Print a message to the screen
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                # Print a message to the screen
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        # Print a message to the screen (Green color)
        self.stdout.write(self.style.SUCCESS('Database available!'))
