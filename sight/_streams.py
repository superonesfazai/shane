from ._utils import (
    extention_to_vcodec, extention_to_acodec, extention_to_scodec,
    )
from ._utils import (
    valid_video_extentions, valid_audio_extentions, valid_subtitle_extentions,
    )


class Stream:
    """A base class of the streams."""
    def __init__(self, raw: dict):
        self._raw = raw  # it's json response from ffprobe
        self.metadata = self._raw.get("tags", {})
        self.container = None

        # defaults
        self._raw["default_filename"] = self._raw.get("filename")
        self._raw["default_codec_name"] = self._raw["codec_name"]

    @property
    def path(self) -> str:
        """The path to the file, if the stream is not inner."""
        return self._raw.get("filename")
    
    @property
    def index(self) -> int:
        """The stream index in the container."""
        return self._raw["index"]

    @property
    def inner(self) -> bool:
        """Indicates whether the stream is some container or not"""
        return self.container is not None

    @property
    def codec(self) -> str:
        """The stream codec."""
        return self._raw["default_codec_name"]

    @property
    def type(self) -> str:
        """The common type of the stream."""
        return self._raw["codec_type"]
    
    @property
    def is_video(self) -> bool:
        return self.type == "video"

    @property
    def is_audio(self) -> bool:
        return self.type == "audio"

    @property
    def is_subtitle(self) -> bool:
        return self.type == "subtitle"

    @property
    def is_data(self) -> bool:
        return self.type == "data"

    @property
    def is_default(self) -> bool:
        """Specifies whether the stream is the default stream"""
        return self._raw["disposition"]["default"] == 1
    
    @codec.setter
    def codec(self, value: str):
        """Property setter for self.codec."""
        if self.is_video:
            if value in vcodecs:
                self._raw["codec_name"] = value
                return
        elif self.is_audio:
            if value in acodecs:
                self._raw["codec_name"] = value
                return
        elif self.is_subtitle:
            if value in scodecs:
                self._raw["codec_name"] = value
                return
        else:
            raise ValueError
    
    @is_default.setter
    def is_default(self, value: bool):
        """Property setter for self.is_default."""
        self._raw["disposition"]["default"] = 1 if value else 0

    @property
    def _codec_if_convert_to(self):
        if self.is_video:
            codec_option = extention_to_vcodec
            possible_extenions = valid_video_extentions
        elif self.is_audio:
            codec_option = extention_to_acodec
            possible_extenions = valid_video_extentions + valid_audio_extentions
        elif self.is_subtitle:
            codec_option = extention_to_scodec
            possible_extenions = valid_video_extentions + valid_subtitle_extentions
        result = {}
        for extention in possible_extenions:
            if self.codec in codec_option[extention]:
                result[extention] = 'copy'
            else:
                result[extention] = codec_option[extention][0]
        return result

    def _make_output_commands(self, i, o, ext):
        """Creates `list` of output options for the stream.

        `i` - input specifier
        `o` - output specifier
        `ext` - output extention
        """
        raise NotImplementedError(
            "You must write `_make_output_commands` \
        method for {self.__class__.__name__}"
        )

    def _add_metadata(self, output_specifier: str):
        """Generates command with output metadata
        
        `o` - output specifier"""
        result = []
        for key, value in self.metadata.items():
            result += [f"-metadata{output_specifier}", f"{key}={value}"]
        return result



class VideoStream(Stream):
    """A video stream."""
    def __init__(self, raw: dict):
        Stream.__init__(self, raw)
        # defaults
        self._raw["default_avg_frame_rate"] = \
        self._raw["avg_frame_rate"] = eval(self._raw["avg_frame_rate"])
        self._raw["default_width"] = self._raw["width"]
        self._raw["default_height"] = self._raw["height"]
    
    @property
    def bitrate(self) -> int: # TODO
        """The number of bits processed per second."""
        raise NotImplementedError

    @property
    def fps(self) -> int:
        """A number of frames per second."""
        return self._raw["avg_frame_rate"]

    @property
    def width(self) -> int:
        """The width of the the video."""
        return self._raw["width"]

    @property
    def height(self) -> int:
        """The height of the the video."""
        return self._raw["height"]

    @fps.setter
    def fps(self, value: float): 
        """Property setter for self.fps."""
        if isinstance(value, float) or isinstance(value, int):
            self._raw["avg_frame_rate"] = value
        else:
            raise TypeError("The fps value must be a number.")

    @width.setter
    def width(self, value: int):
        """Property setter for self.width."""
        if isinstance(value, int):
            self._raw["width"] = value
        else:
            raise TypeError("The width value must be an integer.")

    @height.setter
    def height(self, value: int):
        """Property setter for self.height."""
        if isinstance(value, int):
            self._raw["heigth"] = value
        else:
            raise TypeError("The height value must be an integer.")
    
    def _with_changed_fps(self):
        return self._raw["default_avg_frame_rate"] != self._raw["avg_frame_rate"]

    def _with_chaged_ratio(self):
        return (
            self._raw["default_height"] != self._raw["height"]
            or self._raw["default_width"] != self._raw["width"]
        )

    def _make_output_commands(self, i, o, ext):
        commands = []
        if self._with_changed_fps():
            commands += self._fps_command(i, ext)
        else:
            commands += self._codec_command(i, ext)
        if self._with_chaged_ratio():
            commands += self._ratio_command(i)

        # commands += self._default_command(i)  # TODO
        commands += ["-map", f"{i}:{self.index}"]
        commands += self._add_metadata(output_specifier=f":s:{o}")
        return commands

    def _fps_command(self, i, ext):
        fps_command = f"-r:{i}:{self.index}"
        fps_value = str(self.fps)
        # fps settings and 'stream copy' settings cannot be used together.
        vcodec_command = f"-{self.type[0]}codec:{self.index}"
        if self._codec_if_convert_to[ext] == "copy":
            codec_value = self.codec
        else:
            codec_value = self._codec_if_convert_to[ext]
        return [fps_command, fps_value, vcodec_command, codec_value]

    def _codec_command(self, i, ext):
        codec_command = f"-{self.type[0]}codec:{self.index}"
        codec_value = self._codec_if_convert_to[ext]
        return [codec_command, codec_value]

    def _ratio_command(self, i):
        frame_size_command = f"-s:{i}:{self.index}"
        frame_size_value = f"{self.width}x{self.height}"
        return [frame_size_command, frame_size_value]



class AudioStream(Stream):
    """An audio stream."""
    def __init__(self, raw: dict):
        Stream.__init__(self, raw)
    
    @property
    def channels(self) -> int:
        """The number of channels."""
        return int(self._raw["channels"])

    @property
    def sample_rate(self) -> float:
        """The audio sample rate."""
        return float(self._raw["sample_rate"])

    @property
    def bitrate(self) -> int:
        """The number of bits processed per second."""
        return int(self._raw["bit_rate"])

    @bitrate.setter
    def bitrate(self, value: int):
        """Property setter for self.height."""
        if isinstance(value, int):
            self._raw["bit_rate"] = value
        else:
            raise TypeError("The bitrate value must be an integer.")

    # TODO @sample_rate.setter
    # TODO @channels.setter
   
    def _make_output_commands(self, i, o, ext):
        commands = []
        # TODO: bitrate
        # TODO: channels
        # TODO: sample_rate
        # commands += self._default_command(i) # TODO
        commands += ["-map", f"{i}:{self.index}"]
        commands += self._add_metadata(output_specifier=f":s:{o}")
        return commands



class SubtitleStream(Stream):
    """A subtitle stream."""
    def __init__(self, raw: dict):
        Stream.__init__(self, raw)

    @property
    def is_forced(self) -> bool:
        """Specifies whether subtitles are forced or not."""
        return self._raw["disposition"]["forced"] == 1

    @is_forced.setter
    def is_forced(self, value: bool):
        """Property setter for self.is_forced."""
        self._raw["disposition"]["forced"] = 1 if value is True else 0

    def _make_output_commands(self, i, o, ext):
        commands = []
        # commands += self._forced_command(i) # TODO
        # commands += self._default_command(i) # TODO
        commands += ["-map", f"{i}:{self.index}"]
        commands += self._add_metadata(output_specifier=f":s:{o}")
        return commands



class DataStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError



class ImageStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError