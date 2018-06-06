import os
import json
import subprocess as sp




FFMPEG = os.getenv("FFMPEG_BINARY", "ffmpeg")
FFPROBE = os.getenv("FFPROBE_BINARY", "ffprobe")

ffprobe_command = [FFPROBE, "-loglevel", "panic", "-print_format", "json"]
ffmpeg_command = [FFMPEG, "-y", "-loglevel", "panic"]

valid_video_extentions = [".mkv", ".m4v", ".mp4"]
valid_audio_extentions = [".aac", ".ac3", ".m4a"]
valid_subtitle_extentions = [".srt"]

vcodecs = ['h264']
acodecs = ["aac", "ac3", "flac", "mp3",]
scodecs = ["mov_text", "subrip", "srt", "ass", "ssa", "dvd_subtitle", "vobsub"]

extention_to_vcodec = {".mkv": ["h264"], ".m4v": ["h264"], ".mp4": ["h264"]}
extention_to_scodec = {
    ".mkv": ["subrip", "srt", "ass", "ssa", "dvd_subtitle", "vobsub"],
    ".srt": ["subrip", "srt"],
    # FFmpeg's MP4 muxer does not support sub formats other than mov_text.
    ".m4v": ["mov_text"],
    ".mp4": ["mov_text"],
}
extention_to_acodec = {
    ".mkv": ["aac", "ac3", "flac"],
    ".m4v": ["aac", "alac"],
    ".mp4": ["aac", "alac"],
    ".ac3": ["ac3"],
    ".aac": ["aac"],
    ".m4a": ["aac", "alac"],
}


def make_container(format_, chapters, streams):
    from ._container import Container
    return Container(format_, chapters, streams)


def make_stream(raw):
    from ._streams import VideoStream, AudioStream, SubtitleStream
    if raw["codec_type"] == "video":
        return VideoStream(raw)
    elif raw["codec_type"] == "audio":
        return AudioStream(raw)
    elif raw["codec_type"] == "subtitle":
        return SubtitleStream(raw)
    elif raw["codec_type"] == "data":
        raise NotImplementedError("Not Implemented DataStream.")  # TODO
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
    response = sp.check_output(ffprobe_command + [command, "-i", path])
    return json.loads(response).get(key)
