import os
import json
import subprocess as sp


FFMPEG = os.getenv("FFMPEG_BINARY", "ffmpeg")
FFPROBE = os.getenv("FFPROBE_BINARY", "ffprobe")

FFPROBE_COMMAND = [
    FFPROBE, 
    "-loglevel", "quiet", 
    "-print_format", "json"
]
FFMPEG_COMMAND = [
    FFMPEG, 
    "-loglevel", "quiet",
    ]

# valid output extentions
SUPPORTED_VIDEO_EXTENTIONS = [".mkv", ".m4v", ".mp4"]
SUPPORTED_AUDIO_EXTENTIONS = [".aac", ".ac3", ".m4a"]
SUPPORTED_SUBTITLE_EXTENTIONS = [".srt"]

SUPPORTED_VIDEO_CODECS = ['h264', 'h265']
SUPPORTED_AUDIO_CODECS = ["aac", "ac3", "flac"]
SUPPORTED_SUBTITLE_CODECS = ["mov_text", "subrip", "srt", "ass", "ssa" ]#, "dvd_subtitle", "vobsub"]


CONTAINERS_VCODECS = {
    ".mkv": ["h264", 'h265'], 
    ".m4v": ["h264", 'h265'],
    ".mp4": ["h264", 'h265'],
}

CONTAINERS_ACODECS = {
    ".mkv": ["aac", "ac3", "flac"],
    ".m4v": ["aac", "alac"],
    ".mp4": ["aac", "alac"],
    ".ac3": ["ac3"],
    ".aac": ["aac"],
    ".m4a": ["aac", "alac"],
}

CONTAINERS_SCODECS = {
    ".mkv": ["subrip", "srt", "ass", "ssa", "dvd_subtitle", "vobsub"],
    ".srt": ["subrip", "srt"],
    # FFmpeg's MP4 muxer does not support sub formats other than mov_text.
    ".m4v": ["mov_text"],
    ".mp4": ["mov_text"],
}


FFMPEG_CODEC_FROM_SIGHT = {
    'h265': 'libx265',
}

SIGHT_CODEC_FROM_FFMPEG = {
    'hevc': 'h265',
    # 'libx265': 'h265'
}


class FFmpegNotFoundError(Exception):
    pass



def make_stream(raw):
    from ._streams import (
        VideoStream, 
        AudioStream, 
        SubtitleStream, 
        DataStream
    )
    if raw["codec_type"] == "video":
        return VideoStream(raw)
    elif raw["codec_type"] == "audio":
        return AudioStream(raw)
    elif raw["codec_type"] == "subtitle":
        return SubtitleStream(raw)
    elif raw["codec_type"] == "data":
        return DataStream(raw)
    else:
        raise ValueError("Invalid Stream")


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
    response = sp.check_output(FFPROBE_COMMAND + [command, "-i", path])
    return json.loads(response).get(key)


def check_ffmpeg():
    if not sp.call([FFMPEG, '-loglevel', 'quiet']):
        raise FFmpegNotFoundError("Sight requires FFmpeg installed. ")


class Something:
    """It is either a stream or the container. You can not find out 
    by looking at its `path`."""
    def __init__(self, path):
        self.path = path
        self.format = call_format(path)
        self.streams = call_streams(path)
        self.chapters = call_chapters(path)
        self.first_stream = self.streams[0]
    
    @property
    def is_stream(self):
        return len(self.streams) == 1

    @property
    def is_container(self):
        return len(self.streams) > 1

    def as_stream(self):
        self.first_stream.update(self.format)
        return make_stream(self.first_stream)
    
    def reinit_stream(self) -> dict:
        self.first_stream.update(self.format)
        return self.first_stream
    
    def as_container(self):
        from ._container import Container
        return Container(self.path)