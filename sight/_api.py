import os
from ._utils import (
    call_format, call_streams, 
    call_chapters, make_stream, make_container,
    )

__all__ = ['open']


def open(path):
    if not os.path.exists(path):
        raise ValueError # TODO Error
    format_info = call_format(path)
    streams_info = list(call_streams(path))
    if len(streams_info) > 1:
        # It is a Container object
        chapters_info = list(call_chapters(path))
        streams_info = [make_stream(s) for s in streams_info]
        return make_container(format_info, chapters_info, streams_info)
    else:
        # It is a Stream object
        one_stream_info = streams_info.pop(0)
        one_stream_info.update(format_info)
        return make_stream(one_stream_info)
