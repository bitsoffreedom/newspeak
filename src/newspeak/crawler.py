import logging
logger = logging.getLogger(__name__)

from urlparse import urljoin

import eventlet

# Use Eventlet for parallel processing of HTTP requests
feedparser = eventlet.import_patched('feedparser')

from lxml import html

from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Feed, FeedEntry, FeedContent, FeedEnclosure
from .utils import (
    datetime_from_struct, get_or_create_object, keywords_to_regex, parse_url
)


def extract_xpath(parsed, xpath):
    """
    Extract XPath expression from the HTML at specified URL and return the
    HTML/text representation of its contents, with all links made absolute.

    If parsing fails or the XPath does not resolve an empty string is returned.
    """

    if parsed is None:
        logger.warning(
            u'XPath %s could not be executed because no parsed HTML is available.', xpath
        )

        return ''

    # Execute XPath
    logger.debug(u'Resolving XPath %s', xpath)
    result = parsed.xpath(xpath)

    if not result:
        logger.warning(
            u'XPath %s did not return a value, returning empty string.', xpath
        )

        return ''

    # If the result is already a string, we're done now
    if isinstance(result, basestring):
        return result

    # The result should ideally only contain a single element
    if len(result) > 1:
        logger.warning(
            u'XPath %s returned multiple elements for %s, ignoring all but '
            u' the first.'
        )

    # Take the first element in the XPath result set
    result = result[0]

    # Again, if the result is simply a string, we're done
    if isinstance(result, basestring):
        return result

    # From now on, we will assume it is some HTML element
    assert isinstance(result, html.HtmlMixin)

    # Turn the result into a string
    result = html.tostring(result)

    return result


def filter_entry(feed, entry):
    """
    Return the result of applying filters to a feed entry. True when entry
    is to be included, False if the entry is to be discarded.
    """
    for feed_filter in feed.filters.filter(active=True):
        logger.debug(u'Applying filter %s to entry %s',
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
        logger.debug(u'Discarding entry %s', entry.title)

        # Possible problem: we might want to delete existing entries now
        # that they are filtered. Then again: we might not.
        return

    if 'id' in entry:
        logger.debug(u'Attempt matching by entry ID %s', entry.id)

        db_entry = get_or_create_object(
            FeedEntry, feed=feed, entry_id=entry.id)

    elif 'link' in entry:
        logger.debug(u'Attempt matching by entry link %s', entry.link)

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

    # Only set updated when available - do not assume it to be there
    raw_updated_parsed = getattr(entry, 'updated_parsed', None)
    if raw_updated_parsed:
        db_entry.updated = datetime_from_struct(raw_updated_parsed)

    # Determine whether to perform extraction and if so: only perform it once
    if feed.summary_xpath or feed.enclosure_xpath or feed.content_xpath:
        parsed = parse_url(entry.link)

    # Extraction of summary
    if feed.summary_xpath and (not db_entry.summary or feed.summary_override):
        extracted_summary = extract_xpath(parsed, feed.summary_xpath)

        if extracted_summary:
            # Some value was found, add it to the entry
            db_entry.summary = extracted_summary

            logger.debug(u'Extracted summary for %s from %s',
                db_entry, entry.link
            )

    # Save it to the database
    # (Required before being able to link stuff like content/enclosures)
    db_entry.save()

    # Feed existing content
    if 'content' in entry:
        for entry_content in entry.content:
            # Only add if content with the same mime type and
            # language does not already exist. If it does, update if it differs.
            db_content = get_or_create_object(FeedContent,
                entry=db_entry,
                mime_type=entry_content.type or '',
                language=entry_content.language or ''
            )

            # Update existing content, if differs
            if db_content.value != entry_content.value:
                db_content.value = entry_content.value
                db_content.save()

        logger.debug(u'%d contents added to entry %s',
            len(entry.content), db_entry)

    # Copy existing feed enclosures
    if 'enclosures' in entry:
        for entry_enclosure in entry.enclosures:
            # Only add if an enclosure with the same URL does not
            # already exist
            if FeedEnclosure.objects.filter(
                entry=db_entry, href=entry_enclosure.href).exists():
                logger.debug(
                    u'Enclosure with href \'%s\' already exists, not saving.',
                    entry_enclosure.href
                )

            else:
                # Even though standards require length and mimetype to be set,
                # we are going to assume only href is set - the absolute minimum.
                db_enclosure = FeedEnclosure(
                    entry=db_entry,
                    href=entry_enclosure.href,
                    length=entry_enclosure.length or 0,
                    mime_type=entry_enclosure.type or ''
                )
                db_enclosure.save()

        logger.debug(u'%d enclosures added to entry %s',
            len(entry.enclosures), db_entry)

    # Extraction of content
    if feed.content_xpath:
        extracted_content = extract_xpath(parsed, feed.content_xpath)

        if extracted_content:

            # Only add if content with the same mime type and
            # language does not already exist. If it does, update if it differs.
            db_content = get_or_create_object(FeedContent,
                entry=db_entry,
                mime_type=feed.content_mime_type,
                language=feed.content_language
            )

            # Update existing content, if differs
            if db_content.value != extracted_content:
                db_content.value = extracted_content

                try:
                    db_content.full_clean()

                except ValidationError:
                    # Log the exception, don't save
                    logger.exception(u'Error validating enclosure data.')

                else:
                    # All went fine, saving
                    db_content.save()

                    logger.debug(u'Saved extracted content %s for %s from %s',
                        db_content, db_entry, entry.link
                    )

    # Extraction of enclosures
    if feed.enclosure_xpath:
        extracted_href = extract_xpath(parsed, feed.enclosure_xpath)

        if extracted_href:

            # Make the resulting URL absolute
            extracted_href = urljoin(entry.link, extracted_href)

            # Only add if an enclosure with the same URL does not
            # already exist
            if FeedEnclosure.objects.filter(
                entry=db_entry, href=extracted_href).exists():

                logger.debug(
                    u'Extracted enclosure with href \'%s\' already exists, not saving.',
                    extracted_href
                )

            else:
                db_enclosure = FeedEnclosure(
                    entry=db_entry,
                    href=extracted_href,
                    length=0,
                    mime_type=feed.enclosure_mime_type
                )

                # Validate the results - the URL might be invalid
                try:
                    db_enclosure.full_clean()

                except ValidationError:
                    # Log the exception, don't save
                    logger.exception(u'Error validating enclosure data.')

                else:
                    # All went fine, saving
                    db_enclosure.save()

                    logger.debug(u'Saved extracted enclosure %s for %s from %s',
                        db_enclosure, db_entry, entry.link
                    )


def update_feed(feed):
    """ Update a single feed. """

    logger.info(u'Updating feed %s', feed)

    try:
        # Fetch and parse the feed
        # etag and modified parameters will trigger a conditional GET
        parsed = feedparser.parse(feed.url,\
            etag=feed.etag, modified=feed.modified)

        # Data not changed
        if parsed.status == 304:
            logger.debug(u'Feed %s not changed, aborting', feed)

            return feed

        # Feed gone, disable crawling
        if parsed.status == 410:
            logger.error(u'Feed %s gone, disabling', feed)

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
                u'Feed %s has permanent redirect, updating URL to %s',
                feed, parsed.href)

            feed.url = parsed.href

        # Check for well-formedness
        if parsed.bozo:
            logger.warning(
                u'Feed data was not well-formed. Error: %s',
                unicode(parsed.bozo_exception)
            )

        # Assert the feed id is continuous
        # assert not feed.feed_id or parsed.id == feed.feed_id

        update = True
        if 'updated_parsed' in parsed.feed:
            # Convert feedparser's time_struct to datetime
            parsed_updated = datetime_from_struct(parsed.feed.updated_parsed)

            if feed.updated and feed.updated >= parsed_updated:
                update = False
        else:
            parsed_updated = None

        # Only update if newer
        if update:
            logger.debug(u'Updating feed %s', feed)

            # Update all entries
            for entry in parsed.entries:
                # Only update posts which are changed after the latest feed
                # update - this saves a lot of effort in the filtering
                # process down the road

                entry_update = True
                if 'updated_parsed' in entry:
                    entry_parsed_updated = \
                        datetime_from_struct(entry.updated_parsed)

                    if feed.updated and feed.updated >= entry_parsed_updated:
                        entry_update = False

                if entry_update:
                    logger.debug(u'Updating %s', entry.title)
                    update_entry(feed, entry)
                else:
                    logger.debug(u'Not updating %s', entry.title)

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

                    logger.debug(u'Latest updated entry `%s` at `%s`',
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
            logger.debug(u'Not updating feed %s', feed)

    except Exception as e:
        # Log any exception and pass the status on to the database
        feed.error_state = True
        feed.error_description = unicode(e)
        feed.error_date = now()
        feed.save()

        logger.exception(u'Exception while updating feed %s', feed)

    finally:
        return feed


def update_feeds():
    """ Update all feeds. """

    logger.info(u'Updating all feeds')

    # List all active feeds, randomized ordering for greater concurrency
    feed_qs = Feed.objects.filter(active=True).order_by('?')

    threads = settings.NEWSPEAK_THREADS

    # Create a pool for workers to swim in
    pool = eventlet.GreenPool(size=threads)

    feed_total = feed_qs.count()
    feed_count = 0
    logger.debug(u'Crawling %d feeds with %d lightweight threads.', feed_total, threads)

    for feed in pool.imap(update_feed, feed_qs):
        feed_count += 1
        logger.debug(u'Finished processing feed %s (%d/%d)',
        feed, feed_count, feed_total)

    logger.debug(u'Finished crawling succesfully. %d feeds updated',
        feed_total
    )

    # Wait untill all threads are done
    pool.waitall()
