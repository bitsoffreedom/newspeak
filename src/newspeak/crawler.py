import logging
logger = logging.getLogger(__name__)

from urlparse import urljoin

import eventlet

# Use Eventlet for parallel processing of HTTP requests
feedparser = eventlet.import_patched('feedparser')
from eventlet.green import urllib2

from lxml import html
from lxml.html import HtmlMixin

from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Feed, FeedEntry, FeedContent, FeedEnclosure
from .utils import (
    datetime_from_struct, get_or_create_object, keywords_to_regex
)


def extract_xpath(url, xpath):
    """
    Extract XPath expression from the HTML at specified URL and return the
    HTML/text representation of its contents, with all links made absolute.
    """
    # Fetch and parse
    logger.debug('Fetching and parsing %s', url)

    # Use urllib2 directly for enabled SSL support (LXML doesn't by default)
    opener = urllib2.urlopen(url)

    # Parse
    parsed = html.parse(opener)

    # Execute XPath
    logger.debug('Resolving XPath %s for %s', xpath, url)
    result = parsed.xpath(xpath)

    if not result:
        logger.warning(
            'XPath %s did not return a value for %s, returning empty string.',
            xpath, url)

        return ''

    # If the result is already a string, we're done now
    if isinstance(result, basestring):
        return result

    # The result should ideally only contain a single element
    if len(result) > 1:
        logger.warning(
            'XPath %s returned multiple elements for %s, ignoring all but '
            ' the first.'
        )

    # Take the first element in the XPath result set
    result = result[0]

    # Again, if the result is simply a string, we're done
    if isinstance(result, basestring):
        return result

    # From now on, we will assume it is some HTML element
    assert isinstance(result, HtmlMixin)

    # Make all links in the result absolute
    result.make_links_absolute()

    # Turn the result into a string
    result = html.tostring(result)

    return result


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
        logger.debug('Discarding entry %s', entry.title)

        # Possible problem: we might want to delete existing entries now
        # that they are filtered. Then again: we might not.
        return

    if 'id' in entry:
        logger.debug('Attempt matching by entry ID %s', entry.id)

        db_entry = get_or_create_object(
            FeedEntry, feed=feed, entry_id=entry.id)

    elif 'link' in entry:
        logger.debug('Attempt matching by entry link %s', entry.link)

        db_entry = get_or_create_object(
            FeedEntry, feed=feed, entry_id=None, link=entry.link)

    else:
        raise Exception('Could not identify entry by link or ID.')

    # Copy entry information
    db_entry.title = entry.title
    db_entry.link = entry.link
    db_entry.summary = entry.summary

    db_entry.author = getattr(db_entry, 'author', None)

    db_entry.published = datetime_from_struct(entry.published_parsed)
    db_entry.updated = datetime_from_struct(entry.updated_parsed)

    # Save it to the database
    # (Required before being able to link stuff like content/enclosures)
    db_entry.save()

    # Feed content
    if 'content' in entry:
        for entry_content in entry.content:
            # Even though standards require mimetype to be set,
            # we are going to assume only value is set - the absolute minimum.
            db_content = FeedContent(
                entry=db_entry,
                value=entry_content.value,
                mime_type=entry_content.type or '',
                language=entry_content.language or ''
            )
            db_content.save()

        logger.debug('%d contents added to entry %s',
            len(entry.content), db_entry)

    # Feed enclosures
    if 'enclosures' in entry:
        for entry_enclosure in entry.enclosures:
            # Even though standards require length and mimetype to be set,
            # we are going to assume only href is set - the absolute minimum.
            db_enclosure = FeedEnclosure(
                entry=db_entry,
                href=entry_enclosure.href,
                length=entry_enclosure.length or 0,
                mime_type=entry_enclosure.type or ''
            )
            db_enclosure.save()

        logger.debug('%d enclosures added to entry %s',
            len(entry.enclosures), db_entry)

    # Extraction of enclosures
    if feed.enclosure_xpath:
        extracted_href = extract_xpath(entry.link, feed.enclosure_xpath)

        # Make the resulting URL absolute
        extracted_href = urljoin(entry.link, extracted_href)

        db_enclosure = FeedEnclosure(
            entry=db_entry,
            href=extracted_href,
            length=0,
            mime_type=feed.enclosure_mime_type
        )

        # Validate the results - the URL might be invalid
        try:
            db_enclosure.full_clean()

        except ValidationError as e:
            # Log the exception, don't save
            logger.exception(e)

        else:
            # All went fine, saving
            db_enclosure.save()

            logger.debug('Extracted enclosure %s for %s from %s',
                db_enclosure, db_entry, extracted_href
            )


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
        if 'updated_parsed' in parsed.feed:
            # Convert feedparser's time_struct to datetime
            parsed_updated = datetime_from_struct(parsed.feed.updated_parsed)

            # if feed.updated and feed.updated >= parsed_updated:
            #     update = False
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
                if 'updated_parsed' in entry:
                    entry_parsed_updated = \
                        datetime_from_struct(entry.updated_parsed)

                    # if feed.updated and feed.updated >= entry_parsed_updated:
                    #     entry_update = False

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
                feed.title = getattr(parsed.feed, 'title', 'No title')

            if not feed.subtitle:
                feed.subtitle = getattr(parsed.feed, 'subtitle', '')

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
