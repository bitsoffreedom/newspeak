import logging
logger = logging.getLogger(__name__)

import feedparser

from .models import Feed, FeedEntry
from .utils import datetime_from_struct


def update_entry(feed, entry):
    """ Update a specified entry for the feed. """

    try:
        # Updating an existing object
        db_entry = feed.entries.get(feed=feed, entry_id=entry.id)

        logger.debug('Updating existing entry %s', db_entry)

    except FeedEntry.DoesNotExist:
        # Creating a new object
        db_entry = FeedEntry(feed=feed, entry_id=entry.id)

        logger.debug('Creating new entry %s', db_entry)

    # Determine wheter to update
    # update = True
    # if hasattr(entry, 'updated_parsed'):
    #     parsed_updated = datetime_from_struct(entry.updated_parsed)

    #     if db_entry.updated and db_entry.updated >= parsed_updated:
    #         # Entry is not updated since last parse
    #         update = False

    # if update:
    #     # Copy entry information
    #     db_entry.title = entry.title
    #     db_entry.link = entry.link
    #     db_entry.summary = entry.summary
    #     db_entry.published = datetime_from_struct(entry.published_parsed)
    #     db_entry.updated = parsed_updated

    #     # Save it to the database
    #     db_entry.save()

    # Copy entry information
    db_entry.title = entry.title
    db_entry.link = entry.link
    db_entry.summary = entry.summary
    db_entry.published = datetime_from_struct(entry.published_parsed)
    db_entry.updated = datetime_from_struct(entry.updated_parsed)

    # Save it to the database
    db_entry.save()


def update_feed(feed):
    """ Update a single feed. """

    # Fetch and parse the feed
    parsed = feedparser.parse(feed.url)

    # Check for well-formedness
    if parsed.bozo:
        logger.warning(
            'Feed data was not well-formed. Error: %s',
            unicode(parsed.bozo_exception)
        )

    # Assert the feed id is continuous
    # assert not feed.feed_id or parsed.id == feed.feed_id

    update = True
    if hasattr(parsed.feed, 'updated_parsed'):
        # Convert feedparser's time_struct to datetime
        parsed_updated = datetime_from_struct(parsed.feed.updated_parsed)

        if feed.updated and feed.updated >= parsed_updated:
            update = False
    else:
        parsed_updated = None

    # Only update if newer
    if update:
        logger.debug('Updating feed %s', feed)

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

    else:
        logger.debug('Not updating feed %s', feed)


def update_feeds():
    """ Update all feeds. """

    logger.info('Updating all feeds')

    # List all active feeds
    feed_qs = Feed.objects.filter(active=True)

    for feed in feed_qs:
        logger.info('Updating feed %s', feed)
        update_feed(feed)
