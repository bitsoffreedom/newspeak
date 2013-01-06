import logging
logger = logging.getLogger(__name__)

import re

from time import mktime
from datetime import datetime

from django.utils import timezone
from django.utils.functional import memoize


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
    """ Get or create feed entry with specified kwargs without saving. """

    try:
        # Updating an existing object
        db_entry = model.objects.get(**kwargs)

        logger.debug('Updating existing entry %s', db_entry)

    except model.DoesNotExist:
        # Creating a new object
        db_entry = model(**kwargs)

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

    logger.debug('Compiling regular expression: %s', regex)

    return re.compile(regex)

# Cache the compiled regular expressions - never compile the same twice
_regex_cache = {}
keywords_to_regex = memoize(keywords_to_regex, _regex_cache, 1)
