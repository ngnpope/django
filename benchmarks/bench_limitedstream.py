from itertools import repeat
from io import BytesIO

import pyperf
from django.conf import global_settings as settings
from django.core.handlers.wsgi import LimitedStream


def bench_limitedstream_read(stream, size):
    while stream.read(size):
        pass


def bench_limitedstream_readline(stream, size):
    while stream.readline(size):
        pass


def prepare_stream(lines=1):
    part = b"a=1"
    length = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    chunk_size = length // lines // (1 + len(part))
    generator = (repeat(part, chunk_size) for _ in range(lines))
    data = b"\n".join(b"&".join(x) for x in generator)
    return LimitedStream(BytesIO(data), length)


runner = pyperf.Runner()

runner.bench_func(
    "LimitedStream.read() (single line)",
    bench_limitedstream_read,
    prepare_stream(lines=1),
    None,
)
runner.bench_func(
    "LimitedStream.readline() (single line)",
    bench_limitedstream_readline,
    prepare_stream(lines=1),
    None,
)
runner.bench_func(
    "LimitedStream.read(8192) (single line)",
    bench_limitedstream_read,
    prepare_stream(lines=1),
    8192,
)
runner.bench_func(
    "LimitedStream.readline(8192) (single line)",
    bench_limitedstream_readline,
    prepare_stream(lines=1),
    8192,
)
runner.bench_func(
    "LimitedStream.read() (multiple lines)",
    bench_limitedstream_read,
    prepare_stream(lines=20),
    None,
)
runner.bench_func(
    "LimitedStream.readline() (multiple lines)",
    bench_limitedstream_readline,
    prepare_stream(lines=20),
    None,
)
runner.bench_func(
    "LimitedStream.read(8192) (multiple lines)",
    bench_limitedstream_read,
    prepare_stream(lines=20),
    8192,
)
runner.bench_func(
    "LimitedStream.readline(8192) (multiple lines)",
    bench_limitedstream_readline,
    prepare_stream(lines=20),
    8192,
)
