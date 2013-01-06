from mock import Mock

from django.test import TestCase

from .models import Feed, FeedEntry, KeywordFilter

from .crawler import update_feeds, filter_text, filter_entry


class FetchTests(TestCase):
    """ Tests relating to fetching and parsing of feeds. """

    def test_feed(self):
        """ Test fetching and parsing an Atom feed. """

        feed = Feed(
            url='http://feeds.rijksoverheid.nl/onderwerpen/telecomgegevens-'
                'voor-opsporing/documenten-en-publicaties.rss')

        # Save and fetch
        feed.save()


class BofFeedsTests(TestCase):
    """ Test fetching all feeds in the Bits of Freedom fixture. """

    fixtures = ['feeds_bof']

    def test_fetch(self):
        """
        Update all BOF feeds and make some basic assertions about them.
        """
        update_feeds()

        # Assert entries have been imported
        self.assertTrue(FeedEntry.objects.exists())

        # At least some feeds should have a title and summary
        self.assertTrue(FeedEntry.objects.exclude(title=None).exists())
        self.assertTrue(FeedEntry.objects.exclude(summary=None).exists())

        # Assert for each feed that the updated value makes sense
        updated = False
        for feed in Feed.objects.filter(active=True):
            if feed.entries.filter(updated__isnull=False).exists():
                # Posts exist - updated should match
                self.assertTrue(feed.updated)

                # Make sure the value is at least that of the latest post
                self.assertGreaterEqual(
                    feed.updated, feed.entries.order_by('-updated')[0].updated
                )

                updated = True

        # Make sure at least one feed has it's updated value properly set
        self.assertTrue(updated)


class TextFilterTests(TestCase):
    """ Test the text filter logic. """

    # Some real texts to work with
    text_1 = (
        'Reactie van het Centraal Informatiepunt Onderzoek Telecommunicatie '
        '(CIOT) op het auditrapport &apos;Eindrapport audit CIOT 2011&apos; '
        'van 25 september 2012.'
    )

    text_2 = 'Antwoorden kamervragen over de privacy van internetters'

    text_3 = (
        'Getapte telefoongesprekken tussen verdachten en hun advocaten worden '
        'vanaf volgend jaar automatisch vernietigd. Door een technische '
        'voorziening bij de politie worden de zogenoemde '
        'geheimhoudersgesprekken die plaatsvinden tussen een verdachte -die '
        'in het kader van een strafrechtelijk onderzoek door de politie wordt '
        'getapt- en zijn/haar advocaat, meteen vernietigd en dus niet '
        'opgenomen of afgeluisterd. De advocaat moet daarvoor wel gebruik '
        'maken van vooraf vastgestelde telefoonnummer(s) die bekend zijn bij '
        'de politie. Deze werkwijze betekent dat het vertrouwelijke karakter '
        'van deze gesprekken maximaal wordt gewaarborgd. Dat blijkt uit een '
        'vandaag verschenen brief van minister Hirsch Ballin van Justitie aan '
        'de Tweede Kamer.'
    )

    def test_filter_text_single(self):
        """ Test filter_text with a single keyword. """

        self.assertTrue(filter_text(self.text_2, 'kamervragen'))

        # Matches should be case sensitive
        self.assertTrue(filter_text(self.text_1, 'Reactie'))
        self.assertFalse(filter_text(self.text_1, 'reactie'))

        # Make sure punctuation marks are not counted
        self.assertTrue(filter_text(self.text_3, 'afgeluisterd'))

    def test_filter_text_three(self):
        """ Test filter_text with three keywords. """
        keywords = 'kamervragen, internetters, Reactie'

        self.assertTrue(filter_text(self.text_1, keywords))
        self.assertTrue(filter_text(self.text_2, keywords))
        self.assertFalse(filter_text(self.text_3, keywords))

    def test_filter_text_single_wildcard(self):
        """ Test filter_text with single keyword and wildcards. """

        self.assertTrue(filter_text(self.text_2, 'kamer*'))

        self.assertTrue(filter_text(self.text_1, '?eactie'))
        self.assertTrue(filter_text(self.text_1, '?eactie'))

        self.assertFalse(filter_text(self.text_1, 'hottentottenhutten*'))
        self.assertFalse(filter_text(self.text_1, 'priv*'))

        self.assertTrue(filter_text(self.text_3, '*getapt*'))

    def test_filter_text_three_wildcard(self):
        """ Test filter_text with three keywords and wildcards. """

        keywords = '*vragen, inter*etters, ?eactie'

        self.assertTrue(filter_text(self.text_1, keywords))
        self.assertTrue(filter_text(self.text_2, keywords))
        self.assertFalse(filter_text(self.text_3, keywords))


class EntryFilterTests(TestCase):
    """ Test the entry filter logic. """

    entry_1 = Mock(**{
        'title': u'Toezegging CIOT bevragingen',
        'summary': u''
    })

    entry_2 = Mock(**{
        'title': (
            u'Reactie CIOT op \'Eindrapport audit CIOT 2011\' van '
            u'25 september 2012'
        ),
        'summary': (
            u'Reactie van het Centraal Informatiepunt Onderzoek '
            u'Telecommunicatie (CIOT) op het auditrapport \'Eindrapport '
            u'audit CIOT 2011\' van 25 september 2012.'
        )
    })

    entry_3 = Mock(**{
        'title': (
            u'Indexering tarieven Regeling kosten aftappen en '
            u'gegevensverstrekking - 1 juni 2012 tot 1 juni 2013'
        ),
        'summary': (
            u'Regeling omtrent de indicatieve tarieven voor de periode van '
            u'1 juni 2012 tot 1 juni 2013, genoemd in de bijlage bij de '
            u'Regeling kosten aftappen en gegevensverstrekking.'
        )
    })

    def setUp(self):
        """ Make sure a single feed is available for adding filters. """

        self.feed = Feed(
            url='http://feeds.rijksoverheid.nl/onderwerpen/telecomgegevens-'
                'voor-opsporing/documenten-en-publicaties.rss')

        # Save and fetch
        self.feed.save()

    def test_single_inclusive(self):
        """ Test with a single inclusive filter on title and summary. """

        test_filter = KeywordFilter(
            name='test_filter',
            keywords='CIOT'
        )
        test_filter.save()

        self.feed.filters.add(test_filter)

        self.assertTrue(filter_entry(self.feed, self.entry_1))
        self.assertTrue(filter_entry(self.feed, self.entry_2))
        self.assertFalse(filter_entry(self.feed, self.entry_3))

    def test_single_exclusive(self):
        """ Test with a single exclusive filter on title and summary. """

        test_filter = KeywordFilter(
            name='test_filter',
            keywords='CIOT',
            filter_inclusive=False
        )
        test_filter.save()

        self.feed.filters.add(test_filter)

        self.assertFalse(filter_entry(self.feed, self.entry_1))
        self.assertFalse(filter_entry(self.feed, self.entry_2))
        self.assertTrue(filter_entry(self.feed, self.entry_3))

    def test_single_title_inclusive(self):
        """ Test with a single inclusive filter on just the title. """

        test_filter = KeywordFilter(
            name='test_filter',
            keywords='Indexering'
        )
        test_filter.save()

        self.feed.filters.add(test_filter)

        self.assertFalse(filter_entry(self.feed, self.entry_1))
        self.assertFalse(filter_entry(self.feed, self.entry_2))
        self.assertTrue(filter_entry(self.feed, self.entry_3))

    def test_single_summary_inclusive(self):
        """ Test with a single inclusive filter on just the title. """

        test_filter = KeywordFilter(
            name='test_filter',
            keywords='2012'
        )
        test_filter.save()

        self.feed.filters.add(test_filter)

        self.assertFalse(filter_entry(self.feed, self.entry_1))
        self.assertTrue(filter_entry(self.feed, self.entry_2))
        self.assertTrue(filter_entry(self.feed, self.entry_3))
