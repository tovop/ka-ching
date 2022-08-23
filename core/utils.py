"""
Utility functions.
"""
import datetime


def utc_now():
    """Create an UTC timestamp that includes timezone information."""
    tz = datetime.timezone(datetime.timedelta(hours=0))
    time = datetime.datetime.utcnow().replace(tzinfo=tz)   # timestamp in UTC (incl. time zone information)
    return time
