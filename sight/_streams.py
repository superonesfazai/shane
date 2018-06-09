from ._utils import CONTAINERS_VCODECS, CONTAINERS_ACODECS, CONTAINERS_SCODECS
from ._utils import FFMPEG_CODEC_FROM_SIGHT, SIGHT_CODEC_FROM_FFMPEG
from ._utils import (
    SUPPORTED_VIDEO_CODECS,
    SUPPORTED_AUDIO_CODECS,
    SUPPORTED_SUBTITLE_CODECS,
)
from ._utils import (
    SUPPORTED_VIDEO_EXTENTIONS,
    SUPPORTED_AUDIO_EXTENTIONS,
    SUPPORTED_SUBTITLE_EXTENTIONS,
)

class Stream:
    """A base class of the streams."""
    def __init__(self, raw: dict):
        self._raw = raw  # it's json response from ffprobe
        self.metadata = self._raw.get("tags", {})
        self.container = None

        # defaults
        self._raw["default_filename"] = self._raw.get("filename")
        self._raw["default_codec_name"] = \
        self._raw["codec_name"] = SIGHT_CODEC_FROM_FFMPEG.get(
            self._raw["codec_name"], self._raw["codec_name"])

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
        return self._raw["codec_name"]

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

    @property
    def _default_codec(self):    
        return self._raw["default_codec_name"]

    @codec.setter
    def codec(self, value: str):
        """Property setter for self.codec."""
        error = f"The codec '{value}' is not supported."
        if self.is_video:
            if value in SUPPORTED_VIDEO_CODECS:
                self._raw["codec_name"] = value
            else:
                raise ValueError(error)
        elif self.is_audio:
            if value in SUPPORTED_AUDIO_CODECS:
                self._raw["codec_name"] = value
            else:
                raise ValueError(error)
        elif self.is_subtitle:
            if value in SUPPORTED_SUBTITLE_CODECS:
                self._raw["codec_name"] = value
            else:
                raise ValueError(error)
        else:
            raise ValueError(error)
    
    @is_default.setter
    def is_default(self, value: bool):
        """Property setter for self.is_default."""
        self._raw["disposition"]["default"] = 1 if value else 0

    @property
    def _codec_if_convert_to(self):
        if self.is_video:
            supported_codecs_for = CONTAINERS_VCODECS
            possible_extenions = SUPPORTED_VIDEO_EXTENTIONS
        elif self.is_audio:
            supported_codecs_for = CONTAINERS_ACODECS
            possible_extenions = (
                SUPPORTED_VIDEO_EXTENTIONS + SUPPORTED_AUDIO_EXTENTIONS
            )
        elif self.is_subtitle:
            supported_codecs_for = CONTAINERS_SCODECS
            possible_extenions = (
                SUPPORTED_VIDEO_EXTENTIONS + SUPPORTED_SUBTITLE_EXTENTIONS
            )
        else:
            raise NotImplementedError
        result = {}
        for extention in possible_extenions:
            if self.codec in supported_codecs_for[extention]:
                if self.codec != self._default_codec:
                    result[extention] = FFMPEG_CODEC_FROM_SIGHT.get(
                        self.codec, self.codec)
                else:
                    result[extention] = 'copy'
            else:
                codec = supported_codecs_for[extention][0]
                result[extention] = FFMPEG_CODEC_FROM_SIGHT.get(codec, codec)
        return result

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

    def _make_output_commands(self, i, o, ext, crf):
        # i — input specifier index
        # o — output specifier index
        # ext — extention
        # crf — The Constant Rate Factor
        def _fps_command(i, ext):
            fps_command = f"-r:{i}:{self.index}"
            fps_value = str(self.fps)
            return [fps_command, fps_value]
        
        def _codec_command(i, ext):
            codec_command = f"-{self.type[0]}codec:{self.index}"
            codec_value = self._codec_if_convert_to[ext]
            if self._with_changed_fps() and codec_value == 'copy':
                codec_value = self.codec
            codec_value = FFMPEG_CODEC_FROM_SIGHT.get(codec_value, codec_value)
            return [codec_command, codec_value]        
        
        def _ratio_command(i):
            frame_size_command = f"-s:{i}:{self.index}"
            frame_size_value = f"{self.width}x{self.height}"
            return [frame_size_command, frame_size_value]  
        
        def _vtag_command(ext):
            codec_value = self._codec_if_convert_to[ext]
            codec_value = FFMPEG_CODEC_FROM_SIGHT.get(codec_value, codec_value)

            if codec_value != 'copy':
                codec_name_not_copy = codec_value
            else:
                codec_name_not_copy = FFMPEG_CODEC_FROM_SIGHT.get(self.codec, self.codec)
            
            extention_is_m4v_or_mp4 = (ext == '.m4v' or ext == '.mp4')
            
            codec_is_HEVC = any([
                codec_name_not_copy == 'libx265',
                codec_name_not_copy == 'hevc',
            ])

            if codec_is_HEVC and extention_is_m4v_or_mp4:
                return ['-vtag', 'hvc1'] 
            else:
                return []
        
        def _crf_command(crf):
            if crf:
                return ['-crf', crf]
            else:
                return []
             
        commands = []
        commands += _fps_command(i, ext)
        commands += _codec_command(i, ext)
        commands += _crf_command(crf)
        commands += _ratio_command(i)
        commands += _vtag_command(ext)
        # commands += self._default_command(i)  # TODO
        commands += ["-map", f"{i}:{self.index}"]
        commands += self._add_metadata(output_specifier=f":s:{o}")
        return commands



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
   
    def _make_output_commands(self, i, o, ext, crf):
        def _codec_command(i, ext):
            codec_command = f"-{self.type[0]}codec:{self.index}"
            codec_value = self._codec_if_convert_to[ext]
            codec_value = FFMPEG_CODEC_FROM_SIGHT.get(codec_value, codec_value)
            return [codec_command, codec_value]
        
        commands = []
        # TODO: bitrate
        # TODO: channels
        # TODO: sample_rate
        # commands += self._default_command(i) # TODO
        commands += _codec_command(i, ext)
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

    def _make_output_commands(self, i, o, ext, crf):
        def _codec_command(i, ext):
            codec_command = f"-{self.type[0]}codec:{self.index}"
            codec_value = self._codec_if_convert_to[ext]
            codec_value = FFMPEG_CODEC_FROM_SIGHT.get(codec_value, codec_value)
            return [codec_command, codec_value]
        commands = []
        # commands += self._forced_command(i) # TODO
        # commands += self._default_command(i) # TODO
        commands += _codec_command(i, ext)
        commands += ["-map", f"{i}:{self.index}"]
        commands += self._add_metadata(output_specifier=f":s:{o}")
        return commands
    


class DataStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
        # raise NotImplementedError
    
    def _make_output_commands(self, i, o, ext, crf):
        return []



class ImageStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
        raise NotImplementedError