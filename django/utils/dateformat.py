"""
PHP date() style date formatting
See https://www.php.net/date for format strings

Usage:
>>> from datetime import datetime
>>> d = datetime.now()
>>> df = DateFormat(d)
>>> print(df.format('jS F Y H:i'))
7th October 2003 11:39
>>>
"""
import calendar
from datetime import date, datetime, time, timezone
from email.utils import format_datetime as format_datetime_rfc5322

from django.utils.dates import (
    MONTHS,
    MONTHS_3,
    MONTHS_ALT,
    MONTHS_AP,
    WEEKDAYS,
    WEEKDAYS_ABBR,
)
from django.utils.timezone import (
    _datetime_ambiguous_or_imaginary,
    get_default_timezone,
    is_naive,
    make_aware,
)
from django.utils.translation import gettext as _


class Formatter:
    date_specifiers = frozenset("bcdDEFIjlLmMnNorStUwWyYz")
    time_specifiers = frozenset("aAefgGhHiOPsTuZ")
    all_specifiers = date_specifiers | time_specifiers
    timezone = None

    def __init__(self, obj):
        self.data = obj
        self.type = "datetime"

        if isinstance(obj, datetime):
            # We only support timezone when formatting datetime objects,
            # not date objects (timezone information not appropriate),
            # or time objects (against established django policy).

            if is_naive(obj):
                timezone = get_default_timezone()
            else:
                timezone = obj.tzinfo

            if not _datetime_ambiguous_or_imaginary(obj, timezone):
                self.timezone = timezone

        elif isinstance(obj, date):
            self.type = "date"

    def format(self, formatstr):
        escape = 0
        output = ""

        for char in formatstr:
            if char == "\\":
                escape += 1
                continue

            if escape:
                output += "\\" * (escape // 2)

            if escape % 2 or char not in self.all_specifiers:
                output += char
            elif self.type == "date" and char in self.time_specifiers:
                raise TypeError(
                    "The format for date objects may not contain time-related "
                    f"format specifiers (found {char!r})."
                )
            else:
                output += getattr(self, char)()

            escape = 0

        if escape:
            output += "\\" * (escape // 2 + 1)

        return output

    def a(self):
        "'a.m.' or 'p.m.'"
        if self.data.hour > 11:
            return _("p.m.")
        return _("a.m.")

    def A(self):
        "'AM' or 'PM'"
        if self.data.hour > 11:
            return _("PM")
        return _("AM")

    def b(self):
        "Month, textual, 3 letters, lowercase; e.g. 'jan'"
        return MONTHS_3[self.data.month]

    def c(self):
        """
        ISO 8601 Format
        Example : '2008-01-02T10:30:00.000123'
        """
        return self.data.isoformat()

    def d(self):
        "Day of the month, 2 digits with leading zeros; i.e. '01' to '31'"
        return f"{self.data.day:02d}"

    def D(self):
        "Day of the week, textual, 3 letters; e.g. 'Fri'"
        return WEEKDAYS_ABBR[self.data.weekday()]

    def e(self):
        """
        Timezone name.

        If timezone information is not available, return an empty string.
        """
        if not self.timezone:
            return ""

        try:
            if getattr(self.data, "tzinfo", None):
                return self.data.tzname() or ""
        except NotImplementedError:
            pass
        return ""

    def E(self):
        "Alternative month names as required by some locales. Proprietary extension."
        return MONTHS_ALT[self.data.month]

    def f(self):
        """
        Time, in 12-hour hours and minutes, with minutes left off if they're
        zero.
        Examples: '1', '1:30', '2:05', '2'
        Proprietary extension.
        """
        hour = self.data.hour % 12 or 12
        minute = self.data.minute
        return f"{hour}:{minute:02d}" if minute else f"{hour}"

    def F(self):
        "Month, textual, long; e.g. 'January'"
        return MONTHS[self.data.month]

    def g(self):
        "Hour, 12-hour format without leading zeros; i.e. '1' to '12'"
        hour = self.data.hour % 12 or 12
        return f"{hour}"

    def G(self):
        "Hour, 24-hour format without leading zeros; i.e. '0' to '23'"
        return f"{self.data.hour}"

    def h(self):
        "Hour, 12-hour format; i.e. '01' to '12'"
        hour = self.data.hour % 12 or 12
        return f"{hour:02d}"

    def H(self):
        "Hour, 24-hour format; i.e. '00' to '23'"
        return f"{self.data.hour:02d}"

    def i(self):
        "Minutes; i.e. '00' to '59'"
        return f"{self.data.minute:02d}"

    def I(self):  # NOQA: E743, E741
        "'1' if daylight saving time, '0' otherwise."
        if self.timezone is None:
            return ""
        return "1" if self.timezone.dst(self.data) else "0"

    def j(self):
        "Day of the month without leading zeros; i.e. '1' to '31'"
        return f"{self.data.day}"

    def l(self):  # NOQA: E743, E741
        "Day of the week, textual, long; e.g. 'Friday'"
        return WEEKDAYS[self.data.weekday()]

    def L(self):
        "Boolean for whether it is a leap year; i.e. True or False"
        return str(calendar.isleap(self.data.year))

    def m(self):
        "Month; i.e. '01' to '12'"
        return f"{self.data.month:02d}"

    def M(self):
        "Month, textual, 3 letters; e.g. 'Jan'"
        return MONTHS_3[self.data.month].title()

    def n(self):
        "Month without leading zeros; i.e. '1' to '12'"
        return f"{self.data.month}"

    def N(self):
        "Month abbreviation in Associated Press style. Proprietary extension."
        return MONTHS_AP[self.data.month]

    def o(self):
        "ISO 8601 year number matching the ISO week number (W)"
        return str(self.data.isocalendar()[0])

    def O(self):  # NOQA: E743, E741
        """
        Difference to Greenwich time in hours; e.g. '+0200', '-0430'.

        If timezone information is not available, return an empty string.
        """
        if self.timezone is None:
            return ""

        offset = self.timezone.utcoffset(self.data)
        seconds = offset.days * 86400 + offset.seconds
        sign = "-" if seconds < 0 else "+"
        seconds = abs(seconds)
        minutes = seconds // 60 % 60
        hours = seconds // 3600
        return f"{sign}{hours:02d}{minutes:02d}"

    def P(self):
        """
        Time, in 12-hour hours, minutes and 'a.m.'/'p.m.', with minutes left off
        if they're zero and the strings 'midnight' and 'noon' if appropriate.
        Examples: '1 a.m.', '1:30 p.m.', 'midnight', 'noon', '12:30 p.m.'
        Proprietary extension.
        """
        if self.data.minute == 0 and self.data.hour == 0:
            return _("midnight")
        if self.data.minute == 0 and self.data.hour == 12:
            return _("noon")
        return "%s %s" % (self.f(), self.a())

    def r(self):
        "RFC 5322 formatted date; e.g. 'Thu, 21 Dec 2000 16:01:07 +0200'"
        value = self.data
        if self.type == "date":
            # Assume midnight UTC if instance of datetime.date provided.
            value = datetime.combine(value, time.min).replace(tzinfo=timezone.utc)
        if is_naive(value):
            value = make_aware(value, timezone=self.timezone)
        return format_datetime_rfc5322(value)

    def s(self):
        "Seconds; i.e. '00' to '59'"
        return f"{self.data.second:02d}"

    def S(self):
        """
        English ordinal suffix for the day of the month, 2 characters; i.e.
        'st', 'nd', 'rd' or 'th'.
        """
        if self.data.day in (11, 12, 13):  # Special case
            return "th"
        last = self.data.day % 10
        if last == 1:
            return "st"
        if last == 2:
            return "nd"
        if last == 3:
            return "rd"
        return "th"

    def t(self):
        "Number of days in the given month; i.e. '28' to '31'"
        return str(calendar.monthrange(self.data.year, self.data.month)[1])

    def T(self):
        """
        Time zone of this machine; e.g. 'EST' or 'MDT'.

        If timezone information is not available, return an empty string.
        """
        if self.timezone is None:
            return ""

        return str(self.timezone.tzname(self.data))

    def u(self):
        "Microseconds; i.e. '000000' to '999999'"
        return f"{self.data.microsecond:06d}"

    def U(self):
        "Seconds since the Unix epoch (January 1 1970 00:00:00 GMT)"
        value = self.data
        if self.type == "date":
            value = datetime.combine(value, time.min)
        return str(int(value.timestamp()))

    def w(self):
        "Day of the week, numeric, i.e. '0' (Sunday) to '6' (Saturday)"
        return str((self.data.weekday() + 1) % 7)

    def W(self):
        "ISO-8601 week number of year, weeks starting on Monday"
        return str(self.data.isocalendar()[1])

    def y(self):
        """Year, 2 digits with leading zeros; e.g. '99'."""
        year = self.data.year % 100
        return f"{year:02d}"

    def Y(self):
        """Year, 4 digits with leading zeros; e.g. '1999'."""
        return f"{self.data.year:04d}"

    def z(self):
        """Day of the year, i.e. 1 to 366."""
        return str(self.data.timetuple().tm_yday)

    def Z(self):
        """
        Time zone offset in seconds (i.e. '-43200' to '43200'). The offset for
        timezones west of UTC is always negative, and for those east of UTC is
        always positive.

        If timezone information is not available, return an empty string.
        """
        if self.timezone is None:
            return ""

        offset = self.timezone.utcoffset(self.data)

        # `offset` is a datetime.timedelta. For negative values (to the west of
        # UTC) only days can be negative (days=-1) and seconds are always
        # positive. e.g. UTC-1 -> timedelta(days=-1, seconds=82800, microseconds=0)
        # Positive offsets have days=0
        return str(offset.days * 86400 + offset.seconds)


class TimeFormat(Formatter):
    pass


class DateFormat(TimeFormat):
    pass


def format(value, format_string):
    "Convenience function"
    df = DateFormat(value)
    return df.format(format_string)


def time_format(value, format_string):
    "Convenience function"
    tf = TimeFormat(value)
    return tf.format(format_string)
