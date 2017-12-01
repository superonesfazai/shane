import os

FFMPEG = os.getenv("FFMPEG_BINARY", "ffmpeg")
FFPROBE = os.getenv("FFPROBE_BINARY", "ffprobe")

ffprobe_command = [FFPROBE, "-loglevel", "panic", "-print_format", "json"]
ffmpeg_command = [FFMPEG, "-y", "-loglevel", "panic"]


