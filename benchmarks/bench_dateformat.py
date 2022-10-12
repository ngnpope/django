import inspect
from datetime import datetime, timezone

import pyperf
from django.apps import apps
from django.conf import settings
from django.utils.dateformat import Formatter

# RemovedInDjango51Warning
if not inspect.signature(Formatter).parameters:
    from django.utils.dateformat import DateFormat as Formatter

settings.configure(USE_I18N=True)
apps.populate([])


def bench_formatter_init(value):
    Formatter(value)


def bench_formatter_format(formatter, format_string):
    formatter(format_string)


def bench_formatter_init_and_format(value, format_string):
    Formatter(value).format(format_string)


value = datetime(2022, 7, 23, 17, 19, 43, 26063, tzinfo=timezone.utc)

formats = [
    r"Y. \g\a\d\a j. F",
    r"\N\gà\y d \t\há\n\g n \nă\m Y",
    r"d\u200f/m\u200f/Y",
    r"j\-\a \d\e F YN j, Y, P",
    r"e",
    r"j \d\e F \d\e Y \a \l\e\s G:i",
    r"r",
    r"U",
    r"c",
    r"Z",
    r"d/m/Y D/M/y",
]

runner = pyperf.Runner()

runner.bench_func(
    "Formatter.__init__()",
    bench_formatter_init,
    value,
)
for format_string in formats:
    runner.bench_func(
        f"Formatter.format(): {format_string!r}",
        bench_formatter_format,
        Formatter(value).format,
        format_string,
    )
for format_string in formats:
    runner.bench_func(
        f"Formatter.__init__() & Formatter.format(): {format_string!r}",
        bench_formatter_init_and_format,
        value,
        format_string,
    )
