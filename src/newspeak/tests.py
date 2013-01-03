from django.test import TestCase

from .models import Feed

from .crawler import update_feeds


class FetchTest(TestCase):
    """ Tests relating to fetching and parsing of feeds. """

    # def test_atom_feed(self):
    #   """ Test fetching and parsing an atom feed. """
    #   feed = Feed(url='')

    def test_feed(self):
        """ Test fetching and parsing an Atom feed. """

        feed = Feed(
            url='http://feeds.rijksoverheid.nl/onderwerpen/telecomgegevens-'
                'voor-opsporing/documenten-en-publicaties.rss')

        # Save and fetch
        feed.save()


