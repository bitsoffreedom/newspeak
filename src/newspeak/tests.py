import feedparser

from mock import Mock

from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Feed, FeedEntry, KeywordFilter

from .crawler import update_feeds, filter_entry, keywords_to_regex


class FetchTests(TestCase):
    """ Tests relating to fetching and parsing of feeds. """

    def setUp(self):
        self.rss_url = reverse('rss_all')
        self.atom_url = reverse('atom_all')

    def test_rijksoverheid(self):
        """ Test feed from Rijksoverheid. """

        # Test one feed
        feed = Feed(
            url='http://feeds.rijksoverheid.nl/onderwerpen/telecomgegevens-'
                'voor-opsporing/documenten-en-publicaties.rss')

        # Save and fetch
        feed.save()

        # Assert entries are present
        self.assertTrue(feed.entries.exists())

        # Test requesting the aggregate RSS and Atom feed
        response = self.client.get(self.rss_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(feed.entries.count(), len(parsed.entries))

        response = self.client.get(self.atom_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(feed.entries.count(), len(parsed.entries))

    def test_nrc(self):
        """ Test feed for NRC Handelsblad. """

        # Test one feed
        feed = Feed(url='http://www.nrc.nl/rss.php')

        # Save and fetch
        feed.save()

        # Assert entries are present
        self.assertTrue(feed.entries.exists())

        # Assert some author is present
        self.assertTrue(feed.entries.exclude(author=None).exists())

        # Asssert some content is present
        self.assertTrue(feed.entries.filter(content__isnull=False).exists())

        # Asssert some enclosures are present
        self.assertTrue(feed.entries.filter(enclosures__isnull=False).exists())

        # Test requesting the aggregate RSS and Atom feed
        response = self.client.get(self.rss_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(feed.entries.count(), len(parsed.entries))

        response = self.client.get(self.atom_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(feed.entries.count(), len(parsed.entries))

        # Assert some enclosure is found
        enclosure_found = False
        for entry in parsed.entries:
            if entry.enclosures and entry.enclosures[0].href:
                enclosure_found = True

        self.assertTrue(enclosure_found)

    def test_nytimes(self):
        """ Test feed for NYTimes. """

        # Test one feed
        feed = Feed(
            url='http://www.nytimes.com/services/xml/rss/nyt/GlobalHome.xml')

        # Save and fetch
        feed.save()

        # Assert entries are present
        self.assertTrue(feed.entries.exists())

        # Assert some author is present
        self.assertTrue(feed.entries.exclude(author=None).exists())

        # Test requesting the aggregate RSS and Atom feed
        response = self.client.get(self.rss_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(feed.entries.count(), len(parsed.entries))

        response = self.client.get(self.atom_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(feed.entries.count(), len(parsed.entries))

    def test_nos_podcast(self):
        """ Test podcast NOS Buitenland. """

        # Test one feed
        feed = Feed(url='http://feeds.nos.nl/nospodcastbuitenland')

        # Save and fetch
        feed.save()

        # Assert entries are present
        self.assertTrue(feed.entries.exists())

        # Asssert some enclosures are present
        self.assertTrue(feed.entries.filter(enclosures__isnull=False).exists())

        # Test requesting the aggregate RSS and Atom feed
        response = self.client.get(self.rss_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(feed.entries.count(), len(parsed.entries))

        response = self.client.get(self.atom_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(feed.entries.count(), len(parsed.entries))

    def test_aggregate(self):
        """ Test multiple feed aggregation. """

        # NRC
        feed1 = Feed(url='http://www.nrc.nl/rss.php')
        feed1.save()

        # NOS
        feed2 = Feed(url='http://feeds.nos.nl/nospodcastbuitenland')
        feed2.save()

        # Assert entries are present
        self.assertTrue(FeedEntry.objects.exists())

        # Assert total entries is both feed's entries combined
        self.assertEquals(
            FeedEntry.objects.count(),
            feed1.entries.count() + feed2.entries.count()
        )

        # Assert some author is present
        self.assertTrue(
            FeedEntry.objects.exclude(author=None).exists())

        # Asssert some content is present
        self.assertTrue(
            FeedEntry.objects.filter(content__isnull=False).exists())

        # Asssert some enclosures are present
        self.assertTrue(
            FeedEntry.objects.filter(enclosures__isnull=False).exists())

        # Test requesting the aggregate RSS and Atom feed
        response = self.client.get(self.rss_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(FeedEntry.objects.count(), len(parsed.entries))

        response = self.client.get(self.atom_url)
        parsed = feedparser.parse(response.content)
        self.assertEquals(FeedEntry.objects.count(), len(parsed.entries))


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

        # Perform checks on feeds for which all entries have updated set
        updated_feeds = Feed.objects.filter(
            active=True, entries__updated__isnull=False
        )

        # At least one feed should have entries with updated set
        self.assertTrue(updated_feeds.exists())

        # All of these should adhere to the following condition
        for feed in updated_feeds:
            # Posts exist - updated should match
            self.assertTrue(feed.updated)

            # Make sure the value is at least that of the latest post
            self.assertGreaterEqual(
                feed.updated, feed.entries.order_by('-updated')[0].updated
            )


class RegexFilterTests(TestCase):
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

        self.assertTrue(keywords_to_regex('kamervragen').search(self.text_2))

        # Matches should be case sensitive
        self.assertTrue(keywords_to_regex('Reactie').search(self.text_1))
        self.assertFalse(keywords_to_regex('reactie').search(self.text_1))

        # Make sure punctuation marks are not counted
        self.assertTrue(keywords_to_regex('afgeluisterd').search(self.text_3))

    def test_filter_text_three(self):
        """ Test filter_text with three keywords. """
        keywords = 'kamervragen, internetters, Reactie'
        pattern = keywords_to_regex(keywords)

        self.assertTrue(pattern.search(self.text_1))
        self.assertTrue(pattern.search(self.text_2))
        self.assertFalse(pattern.search(self.text_3))

    def test_filter_text_single_wildcard(self):
        """ Test filter_text with single keyword and wildcards. """

        self.assertTrue(keywords_to_regex('kamer*').search(self.text_2))

        self.assertTrue(keywords_to_regex('*eactie').search(self.text_1))

        self.assertFalse(keywords_to_regex('hottentottenhutten*').search(self.text_1))
        self.assertFalse(keywords_to_regex('priv*').search(self.text_1))

        self.assertTrue(keywords_to_regex('*getapt*').search(self.text_3))

    def test_filter_text_three_wildcard(self):
        """ Test filter_text with three keywords and wildcards. """

        keywords = '*vragen, inter*etters, ?eactie'
        pattern = keywords_to_regex(keywords)

        self.assertTrue(pattern.search(self.text_1))
        self.assertTrue(pattern.search(self.text_2))
        self.assertFalse(pattern.search(self.text_3))


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
