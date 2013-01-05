import logging

from django.core.management.base import BaseCommand

from ...crawler import update_feeds


class Command(BaseCommand):
    help = 'Fetch updated feed data.'
    can_import_settings = True
    requires_model_validation = True

    """
    Map verbosity to log levels, according to: (from Django manual)

    0 means no output.
    1 means normal output (default).
    2 means verbose output.
    3 means very verbose output.
    """
    verbosity_loglevel = {
        '0': logging.ERROR,
        '1': logging.WARNING,
        '2': logging.INFO,
        '3': logging.DEBUG
    }

    def handle(self, *args, **options):
        # Setup the log level for root logger
        loglevel = self.verbosity_loglevel.get(options['verbosity'])
        logging.getLogger('newspeak').setLevel(loglevel)

        update_feeds()
