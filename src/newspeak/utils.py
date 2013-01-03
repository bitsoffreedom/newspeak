from time import mktime
from datetime import datetime

from django.utils import timezone


def datetime_from_struct(time):
    """
    Convert a time_struct to a datetime object.
    Source: http://stackoverflow.com/questions/1697815/how-do-you-convert-a-python-time-struct-time-object-into-a-datetime-object
    """
    dt = datetime.fromtimestamp(mktime(time))

    # Assume this is in the local time zone
    dt = dt.replace(tzinfo=timezone.utc)

    return dt
