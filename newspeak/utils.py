import logging
logger = logging.getLogger(__name__)

import re

from time import mktime
from datetime import datetime

from lxml import html

from eventlet.green import urllib2

from django.utils import timezone
from django.utils.functional import memoize

from django.conf import settings

from django.db import models


def datetime_from_struct(time):
    """
    Convert a time_struct to a datetime object.
    Source: http://stackoverflow.com/questions/1697815/how-do-you-convert-a-python-time-struct-time-object-into-a-datetime-object
    """
    dt = datetime.fromtimestamp(mktime(time))

    # Assume this is in the local time zone
    dt = dt.replace(tzinfo=timezone.utc)

    return dt


def get_or_create_object(model, **kwargs):
    """
    Get or create feed entry with specified kwargs without saving.

    This behaves like Django's own get_or_create but it doesn't save the
    newly created object, allowing for further modification before saving
    without triggering an extra `save()` call.

    Source: https://github.com/visualspace/django-vspace-utils/blob/master/vspace_utils/utils.py
    """

    try:
        # Updating an existing object
        db_entry = model.objects.get(**kwargs)

        logger.debug('Updating existing entry %s', db_entry)

    except model.DoesNotExist:
        # Creating a new object
        db_entry = model(**kwargs)

        logger.debug('Creating new entry %s', db_entry)

    return db_entry


def get_next_ordering(model, field_name='sort_order', increment=10):
    """
    Get the next available value for the sortorder for a model.

    Use case::

        class MyModel(models.Model):
            sort_order = models.PositiveSmallIntegerField(
                default=lambda: get_next_ordering(MyModel)
            )

    Source: https://github.com/visualspace/django-vspace-utils/blob/master/vspace_utils/utils.py
    """
    aggregate = model.objects.aggregate(latest=models.Max(field_name))
    latest = aggregate['latest']

    if latest:
        return latest + increment
    else:
        return increment


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

    logger.debug('Compiling regular expression: %s', regex)

    # Conditionally compile case (in)sensitive
    if settings.NEWSPEAK_CASE_SENSITIVE:
        compiled_regex = re.compile(regex)
    else:
        compiled_regex = re.compile(regex, flags=re.IGNORECASE)

    return compiled_regex

# Cache the compiled regular expressions - never compile the same twice
_regex_cache = {}
keywords_to_regex = memoize(keywords_to_regex, _regex_cache, 1)


def fetch_url(url):
    """ Fetches a URL and returns contents - use opener to support HTTPS. """

    # Fetch and parse
    logger.debug(u'Fetching %s', url)

    # Use urllib2 directly for enabled SSL support (LXML doesn't by default)
    timeout = 30

    try:
        opener = urllib2.urlopen(url, None, timeout)

        # Fetch HTTP data in one batch, as handling the 'file-like' object to
        # lxml results in thread-locking behaviour.
        htmldata = opener.read()

    except urllib2.URLError, urllib2.HTTPError:
        # These type of errors are non-fatal - but *should* be logged.
        logger.exception(u'HTTP Error for %s, returning emtpy string.',
            url
        )

        return None

    return htmldata


def parse_url(url):
    """
    Return lxml-parsed HTML for given URL or None when HTTP request failed.

    Uses urllib2 directly and fetches as string before parsing as to prevent
    thread locking issues.
    """
    htmldata = fetch_url(url)

    # No data, return None
    if not htmldata:
        return None

    # Parse
    logger.debug(u'Parsing HTML for %s', url)
    parsed = html.fromstring(htmldata, base_url=url)

    # Make all links in the result absolute
    parsed.make_links_absolute(url)

    return parsed
