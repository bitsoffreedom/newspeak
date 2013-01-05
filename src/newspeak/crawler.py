import logging
logger = logging.getLogger(__name__)

import eventlet
from eventlet.green import urllib2

import feedparser

from django.utils.timezone import now

from .models import Feed, FeedEntry
from .utils import datetime_from_struct


def get_or_create_entry(**kwargs):
    """ Get or create feed entry with specified kwargs without saving. """

    try:
        # Updating an existing object
        db_entry = FeedEntry.objects.get(**kwargs)

        logger.debug('Updating existing entry %s', db_entry)

    except FeedEntry.DoesNotExist:
        # Creating a new object
        db_entry = FeedEntry(**kwargs)

        logger.debug('Creating new entry %s', db_entry)

    return db_entry


def update_entry(feed, entry):
    """ Update a specified entry for the feed. """

    if hasattr(entry, 'id'):
        logger.debug('Attempt matching by entry ID %s', entry.id)

        db_entry = get_or_create_entry(feed=feed, entry_id=entry.id)

    elif hasattr(entry, 'link'):
        logger.debug('Attempt matching by entry link %s', entry.link)

        db_entry = get_or_create_entry(feed=feed, entry_id=None, link=entry.link)

    else:
        raise Exception('Could not identify entry by link or ID.')


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

    logger.info('Updating feed %s', feed)

    try:
        # Fetch and parse the feed
        rawdata = urllib2.urlopen(feed.url).read()
        parsed = feedparser.parse(rawdata)

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

            # Clear any possible error state
            feed.error_state = False

            feed.save()

        else:
            logger.debug('Not updating feed %s', feed)

    except Exception as e:
        # Log any exception and pass the status on to the database
        feed.error_state = True
        feed.error_description = unicode(e)
        feed.error_date = now()
        feed.save()

        logger.exception(e)

    finally:
        return feed


def update_feeds():
    """ Update all feeds. """

    logger.info('Updating all feeds')

    # List all active feeds, randomized ordering for greater concurrency
    feed_qs = Feed.objects.filter(active=True).order_by('?')

    # Create a pool with 16 workers to swim in
    pool = eventlet.GreenPool(size=16)

    for feed in pool.imap(update_feed, feed_qs):
        logger.debug('Finished processing feed %s', feed)

    # Wait untill all threads are done
    pool.waitall()
