"""What counts as "tonight".

A night starts at CHAT_NIGHT_START_HOUR (default 18, i.e. 6 PM) in your site's
TIME_ZONE and lasts until the next one begins. Everything made since the most
recent start is "tonight"; everything made before it belongs to the archive.
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


def _hour():
    return getattr(settings, 'CHAT_NIGHT_START_HOUR', 18)


def tonight_start(now=None):
    now = timezone.localtime(now or timezone.now())
    start = now.replace(hour=_hour(), minute=0, second=0, microsecond=0)
    if now < start:
        start -= timedelta(days=1)
    return start


def night_of(moment):
    """The calendar date of the evening the night started on."""
    return (timezone.localtime(moment) - timedelta(hours=_hour())).date()
