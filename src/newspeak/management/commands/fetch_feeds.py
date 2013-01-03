from django.core.management import call_command
from django.core.management.base import BaseCommand

from optparse import make_option


class Command(BaseCommand):
    help = 'Fetch updated feed data.'

    def handle(self, *args, **options):
        # Call fetch mechanism
        pass
