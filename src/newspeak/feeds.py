from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed


from .models import FeedEntry


class NewspeakFeedMixin(object):
    """ Aggregate RSS Feed for Newspeak. """

    title = "Newspeak van de Nederlandse overheid"
    link = "/"
    description = (
        'De Nederlandse overheid en het parlement publiceren veel documenten,'
        ' zoals kamerstukken, persberichten en brochures. De Newspeak RSS '
        'feed haalt de krenten uit de pap.'
    )
    author_name = 'Rejo Zenger'
    author_email = 'rejo@zenger.nl'
    author_link = \
        'https://rejo.zenger.nl/inzicht/newspeak-van-de-nederlandse-overheid/'

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
    # To be Done


class Content(object):
    """
    Represents Atom content - modelled after Enclosure
    in django/utils/feedgenerator.py
    """
    def __init__(self, value, mime_type, language):
        "All args are expected to be Python Unicode objects"
        self.value, self.mime_type, self.language = \
            value, mime_type, language


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


class ExtendedAtomFeed(Atom1Feed):
    """ Atom feed with extensions. """

    def add_item_elements(self, handler, item):
        super(ExtendedAtomFeed, self).add_item_elements(handler, item)

        # Content
        if item['content'] is not None:
            handler.addQuickElement("content", '',
                {"value": item['content'].value,
                 "mime_type": item['content'].mime_type,
                 "language": item['content'].language})


class NewspeakRSSFeed(NewspeakFeedMixin, Feed):
    """ RSS variant of Newspeak Feed. """

    feed_type = ExtendedRSSFeed


class NewspeakAtomFeed(NewspeakRSSFeed):
    """ Atom variant of Newspeak Feed. """

    feed_type = ExtendedAtomFeed
    subtitle = NewspeakRSSFeed.description

