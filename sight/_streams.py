


class Stream:
    """A base class of the streams."""
    def __init__(self, raw):
        self._raw = raw  # it's json response from ffprobe
        self.metadata = self._raw.get("tags", {})
        # defaults
        self._raw["default_filename"] = self._raw.get("filename")
        self._raw["default_codec_name"] = self._raw["codec_name"]

    @property
    def index(self):
        """The stream index in the container."""
        return self._raw["index"]

    @property
    def codec(self):
        """The stream codec."""
        return self._raw["default_codec_name"]

    @property
    def type(self):
        """The common type of the stream."""
        return self._raw["codec_type"]
    
    @property
    def is_video(self):
        return self.type == "video"

    @property
    def is_audio(self):
        return self.type == "audio"

    @property
    def is_subtitle(self):
        return self.type == "subtitle"

    @property
    def is_data(self):
        return self.type == "data"

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
        # defaults
        self._raw["default_avg_frame_rate"] = \
        self._raw["avg_frame_rate"] = eval(self._raw["avg_frame_rate"])
        self._raw["default_width"] = self._raw["width"]
        self._raw["default_height"] = self._raw["height"]
    
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

    @fps.setter
    def fps(self, value): 
        """Property setter for self.fps."""
        if isinstance(value, float) or isinstance(value, int):
            self._raw["avg_frame_rate"] = value
        else:
            raise TypeError("The fps value must be a number.")

    @width.setter
    def width(self, value):
        """Property setter for self.width."""
        if isinstance(value, int):
            self._raw["width"] = value
        else:
            raise TypeError("The width value must be an integer.")

    @height.setter
    def height(self, value):
        """Property setter for self.height."""
        if isinstance(value, int):
            self._raw["heigth"] = value
        else:
            raise TypeError("The height value must be an integer.")



class AudioStream(Stream):
    """An audio stream."""
    def __init__(self, raw):
        Stream.__init__(self, raw)
    
    @property
    def channels(self):
        """The number of channels."""
        return int(self._raw["channels"])

    @property
    def sample_rate(self):
        """The audio sample rate."""
        return float(self._raw["sample_rate"])

    @property
    def bitrate(self):
        """The number of bits processed per second."""
        return int(self._raw["bit_rate"])

    @bitrate.setter
    def bitrate(self, value):
        """Property setter for self.height."""
        if isinstance(value, int):
            self._raw["bit_rate"] = value
        else:
            raise TypeError("The bitrate value must be an integer.")

    # TODO @sample_rate.setter
    # TODO @channels.setter



class SubtitleStream(Stream):
    """A subtitle stream."""
    def __init__(self, raw):
        Stream.__init__(self, raw)

    @property
    def is_forced(self):
        """Specifies whether subtitles are forced or not."""
        return self._raw["disposition"]["forced"] == 1

    @is_forced.setter
    def is_forced(self, value):
        """Property setter for self.is_forced."""
        self._raw["disposition"]["forced"] = 1 if value is True else 0




class DataStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError



class ImageStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError