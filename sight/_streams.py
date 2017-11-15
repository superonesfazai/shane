


class Stream:
    """A base class of the streams."""
    def __init__(self, raw):
        self._raw = raw  # it's json response from ffprobe
        self.metadata = self._raw.get("tags", {})

    @property
    def index(self):
        """The stream index in the container."""
        return self._raw["index"]

    @property
    def codec(self):
        """The stream codec."""
        return self._raw["codec_name"]

    @property
    def type(self):
        """The common type of the stream."""
        return self._raw["codec_type"]

    @property
    def is_default(self):
        """Specifies whether the stream is the default stream"""
        return self._raw["disposition"]["default"] == 1

    @is_default.setter
    def is_default(self, value: bool):
        """Property setter for self.is_default."""
        self._raw["disposition"]["default"] = 1 if value else 0



class VideoStream(Stream):
    """A video stream."""
    def __init__(self, raw):
        Stream.__init__(self, raw)
    
    @property
    def bitrate(self): # TODO
        """The number of bits processed per second."""
        raise NotImplementedError

    @property
    def fps(self):
        """A number of frames per second."""
        return self._raw["avg_frame_rate"]

    @property
    def width(self):
        """The width of the the video.""""
        return self._raw["width"]

    @property
    def height(self):
        """The height of the the video.""""
        return self._raw["height"]



class AudioStream(Stream):
    """An audio stream."""
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError



class SubtitleStream(Stream):
    """A subtitle stream."""
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError



class DataStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError



class ImageStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError