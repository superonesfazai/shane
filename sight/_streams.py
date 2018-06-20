import os
import subprocess as sp

from ._ffmpeg import FFmpegCompressor
from ._utils import (
    IMAGES_CODECS, 
    SIGHT_CODEC_FROM_FFMPEG,
    
    SUPPORTED_AUDIO_EXTENTIONS,
    SUPPORTED_SUBTITLE_EXTENTIONS,
    SUPPORTED_VIDEO_EXTENTIONS, 
    
    Something
)


class StreamError(Exception):
    pass


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
        self._raw['default_filename'] = \
        self._raw['filename'] = self._raw.get('filename')

        self._commands_history = set()

    def _init(self, path):
        something = Something(path)
        self._raw = something.reinit_stream()
        self.metadata = self._raw.get("tags", {})
        self.container = None
        # defaults
        self._raw["default_filename"] = self._raw.get("filename")
        self._raw["default_codec_name"] = \
        self._raw["codec_name"] = SIGHT_CODEC_FROM_FFMPEG.get(
            self._raw["codec_name"], self._raw["codec_name"])
        self._raw['default_filename'] = \
        self._raw['filename'] = self._raw.get('filename')
    
    @property
    def is_container(self) -> bool:
        return not isinstance(self, Stream)
    
    @property
    def path(self) -> str:
        """The path to the file, if the stream is not inner."""
        return self._raw["filename"]

    @property
    def default_path(self):
        return self._raw['default_filename']

    @property
    def extention(self):
        """The stream extention."""
        if self._raw["filename"]:
            return os.path.splitext(self._raw["filename"])[-1]
        else:
            return None

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
        return self.type == "video" and self.codec not in IMAGES_CODECS

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
    def is_attachment(self) -> bool:
        return self.type == 'attachment'

    @property
    def is_image(self) -> bool:
        self.type == "video" and self.codec in IMAGES_CODECS 
    
    @property
    def is_default(self) -> bool:
        """Specifies whether the stream is the default stream"""
        return self._raw["disposition"]["default"] == 1

    @property
    def _default_codec(self):    
        return self._raw["default_codec_name"]

    @path.setter
    def path(self, path):
        """Property setter for self.path."""
        if self.inner == True:
            raise AttributeError("An inner stream can not have a path")
        if os.path.exists(path):
            raise ValueError(f"The path '{path}' already exists")
        self._raw["filename"] = path

    @extention.setter
    def extention(self, ext):
        """Property setter for self.extention."""
        if self.inner == True:
            raise AttributeError("An inner stream can not have an extention")
        if self.is_video:
            supported_extentions = SUPPORTED_VIDEO_EXTENTIONS
        elif self.is_audio:
            supported_extentions = SUPPORTED_AUDIO_EXTENTIONS
        elif self.is_subtitle:
            supported_extentions = SUPPORTED_SUBTITLE_EXTENTIONS
        else:
            raise NotImplementedError
        if ext in supported_extentions:
            root, _ = os.path.splitext(self.path)
            self.path = root + ext
        else:
            raise ValueError(f"The extention '{ext}' is not supported.")

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

    def save(self, **settings):
        """Saves all the changes. Only for outer streams"""
        if self.inner:
            raise StreamError # TODO Error
        compressor = FFmpegCompressor()
        compressor.add_input_files(self)
        compressor.add_output_path(self.path)
        compressor.add_settings(**settings)
        response = compressor.run()
        self._init(self.path)
        return response

    def extract(self, path=None, **settings):
        """Extreacts the stream and saves it to the `path`. Returns 
         the extracted stream"""
        if not self.inner:
            raise StreamError # TODO Error
        compressor = FFmpegCompressor()
        compressor.add_input_files(self.container)
        compressor.add_output_path(path)
        compressor.add_settings(**settings)
        compressor.extract_stream_run(self)
        something = Something(path)
        return something.as_stream()



class VideoStream(Stream):
    """A video stream."""
    def __init__(self, raw: dict):
        Stream.__init__(self, raw)
        # defaults
        if self._raw.get("avg_frame_rate", '0/0') != '0/0' :
            self._raw["default_avg_frame_rate"] = \
            self._raw["avg_frame_rate"] = eval(self._raw["avg_frame_rate"])
        else:
            self._raw["default_avg_frame_rate"] = \
            self._raw["avg_frame_rate"] = 0
        
        self._raw["default_width"] = self._raw["width"]
        self._raw["default_height"] = self._raw["height"]

    def _init(self, path):
        Stream._init(self, path)
        # defaults
        self._raw["default_avg_frame_rate"] = \
        self._raw["avg_frame_rate"] = eval(self._raw["avg_frame_rate"])
        self._raw["default_width"] = self._raw["width"]
        self._raw["default_height"] = self._raw["height"]        

    # @property
    # def bitrate(self) -> int: # TODO
    #     """The number of bits processed per second."""
    #     raise NotImplementedError

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
            self._raw["height"] = value
        else:
            raise TypeError("The height value must be an integer.")
    
    def with_changed_fps(self):
        return self._raw["default_avg_frame_rate"] != self._raw["avg_frame_rate"]

    def with_changed_frame_size(self):
        return (
            self._raw["default_height"] != self._raw["height"]
            or self._raw["default_width"] != self._raw["width"]
        )

    def __repr__(self):
        return (self.__class__.__name__ + "("
            f"path={self.path}, codec={self.codec}, fps={self.fps}, " + 
            f"width={self.width}, height={self.height}, " +
            f"language={self.metadata.get('language')}" +
            ")"
        )



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

    # TODO @sample_rate.setter
    # TODO @channels.setter

    def __repr__(self):
        return (self.__class__.__name__ + "("
            f"path={self.path}, codec={self.codec}, channels={self.channels}, " + 
            f"sample_rate={self.sample_rate}, " +
            f"language={self.metadata.get('language')}" +
            ")"
        )



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

    def __repr__(self):
        return (self.__class__.__name__ + "("
            f"path={self.path}, codec={self.codec}, is_forced={self.is_forced}, " + 
            f"language={self.metadata.get('language')}" +
            ")"
        )



class DataStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)



class ImageStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)



class AttachmentStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw) 

    def __repr__(self):
        return (self.__class__.__name__ + "("
            f"path={self.path}, codec={self.codec}, " + 
            f"language={self.metadata.get('language')}" +
            ")"
        )
