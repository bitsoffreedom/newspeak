import feedparser
import datetime

from .models import Feed, FeedEntry
from .utils import datetime_from_struct


def update_entry(feed, entry):
    """ Update a specified entry for the feed. """

    try:
        # Updating an existing object
        db_entry = feed.entries.get(feed=feed, entry_id=entry.id)
    except FeedEntry.DoesNotExist:
        # Creating a new object
        db_entry = FeedEntry(feed=feed, entry_id=entry.id)

    # Copy entry information
    db_entry.title = entry.title
    db_entry.link = entry.link
    db_entry.published = datetime_from_struct(entry.published_parsed)
    db_entry.updated = datetime_from_struct(entry.updated_parsed)

    # Save it to the database
    db_entry.save()


def update_feed(feed):
    """ Update a single feed. """

    # Fetch and parse the feed
    parsed = feedparser.parse(feed.url)

    # Assert the feed id is continuous
    # assert not feed.feed_id or parsed.id == feed.feed_id

    # Convert feedparser's time_struct to datetime
    parsed_updated = datetime_from_struct(parsed.feed.updated_parsed)

    # Only update if newer
    if not feed.updated or feed.updated < parsed_updated:
        # Update all entries
        for entry in parsed.entries:
            update_entry(feed, entry)

        # Make sure the feed ID and last update are synchronized
        # feed.feed_id = parsed.id
        feed.updated = parsed_updated

        # Set title and subtitle only if not already set
        if not feed.title:
            feed.title = parsed.feed.title

        if not feed.subtitle:
            feed.subtitle = parsed.feed.subtitle

        feed.save()

def update_feeds():
    """ Update all feeds. """

    # List all active feeds
    feed_qs = Feed.objects.filter(active=True)

    for feed in feed_qs:
        update_feed(feed)
