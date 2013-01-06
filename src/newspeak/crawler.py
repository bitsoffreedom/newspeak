import logging
logger = logging.getLogger(__name__)

import re

import eventlet

feedparser = eventlet.import_patched('feedparser')

from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

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


def keywords_to_regex(keywords):
    """ Take keywords, return compiled regex. """

    regex_parts = []
    # Construct regex for keyword filter
    for keyword in keywords.split(','):
        # Strip leading or trailing spaces from keyword
        keyword = keyword.strip()

        keyword = keyword.replace('*', '\w*')
        keyword = keyword.replace('?', '\w')

        regex_parts.append(keyword)

    regex = '|'.join(regex_parts)

    logger.debug('Constructed regular expression: %s', regex)

    return re.compile(regex)


def filter_entry(feed, entry):
    """
    Return the result of applying filters to a feed entry. True when entry
    is to be included, False if the entry is to be discarded.
    """
    for feed_filter in feed.filters.filter(active=True):
        logger.debug('Applying filter %s to entry %s',
            feed_filter, entry.title
        )

        pattern = keywords_to_regex(feed_filter.keywords)

        if feed_filter.filter_inclusive:
            # Keep only matched entries

            if feed_filter.filter_title and \
                pattern.search(entry.title):

                # Pass: process next filter
                break

            if feed_filter.filter_summary and \
                pattern.search(entry.summary):

                # Pass: process next filter
                break

            # No match: discard entry
            return False

        else:
            # Exclusive filtering - discard matching entries
            if feed_filter.filter_title and \
                pattern.search(entry.title):

                # Match: discard this entry
                return False

            if feed_filter.filter_summary and \
                pattern.search(entry.summary):

                # Match: discard this entry
                return False

    # By default, include all entries
    return True


def update_entry(feed, entry):
    """ Update a specified entry for the feed. """

    # Consider whether or not to discard the item
    if not filter_entry(feed, entry):
        # Entry to be discarded - stop further processing

        # Possible problem: we might want to delete existing entries now
        # that they are filtered. Then again: we might not.
        return

    if hasattr(entry, 'id'):
        logger.debug('Attempt matching by entry ID %s', entry.id)

        db_entry = get_or_create_entry(feed=feed, entry_id=entry.id)

    elif hasattr(entry, 'link'):
        logger.debug('Attempt matching by entry link %s', entry.link)

        db_entry = get_or_create_entry(feed=feed, entry_id=None, link=entry.link)

    else:
        raise Exception('Could not identify entry by link or ID.')

    # Copy entry information
    db_entry.title = entry.title
    db_entry.link = entry.link
    db_entry.summary = entry.summary

    if hasattr(entry, 'author'):
        db_entry.author = entry.author

    db_entry.published = datetime_from_struct(entry.published_parsed)
    db_entry.updated = datetime_from_struct(entry.updated_parsed)

    # Save it to the database
    db_entry.save()


def update_feed(feed):
    """ Update a single feed. """

    logger.info('Updating feed %s', feed)

    try:
        # Fetch and parse the feed
        # etag and modified parameters will trigger a conditional GET
        parsed = feedparser.parse(feed.url,\
            etag=feed.etag, modified=feed.modified)

        # Data not changed
        if parsed.status == 304:
            logger.debug('Feed %s not changed, aborting', feed)

            return feed

        # Feed gone, disable crawling
        if parsed.status == 410:
            logger.error('Feed %s gone, disabling', feed)

            feed.error_state = True
            feed.error_description = _(
                'Feed returns 410: Gone. Crawling deactivated.'
            )
            feed.active = False
            feed.save()

            return feed

        # Permanent redirect, update URL
        if parsed.status == 301:
            logger.warning(
                'Feed %s has permanent redirect, updating URL to %s',
                feed, parsed.href)

            feed.url = parsed.href

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
                # Only update posts which are changed after the latest feed
                # update - this saves a lot of effort in the filtering
                # process down the road

                entry_update = True
                if hasattr(entry, 'updated_parsed'):
                    entry_parsed_updated = \
                        datetime_from_struct(entry.updated_parsed)

                    if feed.updated and feed.updated >= entry_parsed_updated:
                        entry_update = False

                if entry_update:
                    logger.debug('Updating %s', entry.title)
                    update_entry(feed, entry)
                else:
                    logger.debug('Not updating %s', entry.title)

            # Make sure the feed ID is synchronized
            # feed.feed_id = parsed.id

            if parsed_updated:
                # Get latest update from feed
                feed.updated = parsed_updated

            else:
                # Get latest update from database
                updated_entries = feed.entries.filter(updated__isnull=False)

                try:
                    latest = updated_entries.order_by('-updated')[0]

                    logger.debug('Latest updated entry `%s` at `%s`',
                        latest, latest.updated)

                    feed.updated = latest.updated

                except IndexError:
                    # No entries exist in feed or none have updated set
                    feed.updated = None

            # Set title and subtitle only if not already set
            if not feed.title:
                feed.title = parsed.feed.title

            if not feed.subtitle:
                feed.subtitle = parsed.feed.subtitle

            # Clear any possible error state
            feed.error_state = False

            # Store last modified and etag
            feed.etag = getattr(parsed, 'etag', '')
            feed.modified = getattr(parsed, 'modified', '')

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
