from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed

from django.conf import settings

from .models import FeedEntry


class NewspeakFeedMixin(object):
    """ Aggregate RSS Feed for Newspeak. """

    # Get feed metadata from Django settings
    title = settings.NEWSPEAK_METADATA['title']
    link = settings.NEWSPEAK_METADATA['link']
    description = settings.NEWSPEAK_METADATA['description']
    author_name = settings.NEWSPEAK_METADATA['author_name']
    author_email = settings.NEWSPEAK_METADATA['author_email']
    author_link = settings.NEWSPEAK_METADATA['author_link']

    def items(self):
        """ Return a queryset of all feed items to display. """
        feed_qs = FeedEntry.objects.all()

        # Only show active feeds
        feed_qs = feed_qs.filter(feed__active=True)

        # Make unique by link (post ID is not reliable)
        feed_qs = feed_qs.distinct()

        # Order descending by publication date
        feed_qs = feed_qs.order_by('-published')

        # Only return latest 150 elements
        feed_qs = feed_qs[:150]

        return feed_qs

    def item_title(self, obj):
        return obj.title

    def item_description(self, obj):
        return obj.summary

    def item_link(self, obj):
        return obj.link

    def item_author(self, obj):
        return obj.author

    def item_pubdate(self, obj):
        return obj.published

    # Enclosures: for now, render just the first enclosure
    def item_enclosure_url(self, obj):
        try:
            return obj.enclosures.all()[0].href
        except IndexError:
            return None

    def item_enclosure_length(self, obj):
        try:
            return obj.enclosures.all()[0].length
        except IndexError:
            return None

    def item_enclosure_mime_type(self, obj):
        try:
            return obj.enclosures.all()[0].mime_type
        except IndexError:
            return None

    # Extra feed items
    def item_extra_kwargs(self, obj):
        return dict(content=Content(
            value=self.item_content_value(obj),
            mime_type=self.item_content_mime_type(obj),
            language=self.item_content_language(obj)
        ), source=Source(
            title=self.item_source_title(obj),
            link=self.item_source_link(obj)
        ))

    # Content: for now, render just the first content element
    def item_content_value(self, obj):
        try:
            return obj.content.all()[0].value
        except IndexError:
            return None

    def item_content_mime_type(self, obj):
        try:
            return obj.content.all()[0].mime_type
        except IndexError:
            return None

    def item_content_language(self, obj):
        try:
            return obj.content.all()[0].language
        except IndexError:
            return None

    # Source
    def item_source_title(self, obj):
        return obj.feed.title

    def item_source_link(self, obj):
        return obj.feed.url


class Content(object):
    """
    Represents Atom content - modelled after Enclosure
    in django/utils/feedgenerator.py
    """
    def __init__(self, value, mime_type, language):
        "All args are expected to be Python Unicode objects"
        self.value, self.mime_type, self.language = \
            value, mime_type, language


class Source(object):
    """
    Source feed.
    """
    def __init__(self, title, link):
        self.title, self.link = title, link


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    RSS feed with extensions.
    """

    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)

        # Content
        if item['content'] is not None:
            handler.addQuickElement(
                'content:encoded', item['content'].value
            )

        # Source link
        if item['source'] is not None:
            handler.addQuickElement(
                'source', item['source'].title, {'url': item['source'].link}
            )


class ExtendedAtomFeed(Atom1Feed):
    """ Atom feed with extensions. """

    def add_item_elements(self, handler, item):
        super(ExtendedAtomFeed, self).add_item_elements(handler, item)

        # Content
        if item['content'] is not None:
            attrs = {}

            if item['content'].mime_type:
                attrs.update({'mime_type': item['content'].mime_type})

            if item['content'].language:
                attrs.update({'language': item['content'].language})

            handler.addQuickElement("content", item['content'].value, attrs)

        # Source link
        if item['source'] is not None:
            handler.startElement('source', {})

            handler.addQuickElement('title', item['source'].title)
            handler.addQuickElement('url', item['source'].link)

            handler.endElement('source')


class NewspeakRSSFeed(NewspeakFeedMixin, Feed):
    """ RSS variant of Newspeak Feed. """

    feed_type = ExtendedRSSFeed


class NewspeakAtomFeed(NewspeakRSSFeed):
    """ Atom variant of Newspeak Feed. """

    feed_type = ExtendedAtomFeed
    subtitle = NewspeakRSSFeed.description
