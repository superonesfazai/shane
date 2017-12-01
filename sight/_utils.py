import os
import json
import subprocess as sp


FFMPEG = os.getenv("FFMPEG_BINARY", "ffmpeg")
FFPROBE = os.getenv("FFPROBE_BINARY", "ffprobe")

ffprobe_command = [FFPROBE, "-loglevel", "panic", "-print_format", "json"]
ffmpeg_command = [FFMPEG, "-y", "-loglevel", "panic"]


def call_streams(path):
    return _call_ffprobe("streams", path)


def call_format(path):
    return _call_ffprobe("format", path)


def call_chapters(path):
    return _call_ffprobe("chapters", path)
    for chapter in response:
        yield {
            "title": chapter.get("title"),
            "start": float(chapter.get("start_time")),
            "end": float(chapter.get("end_time")),
        }


def _call_ffprobe(show_what, path):
    if show_what == "streams":
        command = "-show_streams"
        key = "streams"
    elif show_what == "format":
        command = "-show_format"
        key = "format"
    else:
        command = "-show_chapters"
        key = "chapters"
    response = sp.check_output(ffprobe_command + [command, "-i", path])
    return json.loads(response).get(key)
