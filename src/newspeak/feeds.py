from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed


from .models import FeedEntry


class NewspeakRSSFeed(Feed):
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

    # def item_enclosure_url(self, obj):
    #     pass

    # def item_enclosure_length(self, obj):
    #     pass

    # def item_enclosure_mime_type(self, obj):
    #     pass


class NewspeakAtomFeed(NewspeakRSSFeed):
    """ Atom variant of RSS Feed. """
    feed_type = Atom1Feed
    subtitle = NewspeakRSSFeed.description
