import os
import math
import subprocess as sp
from ._utils import SUPPORTED_VIDEO_EXTENTIONS
from ._ffmpeg import FFmpegCompressor


class Container:
    """A Container wraps a file that contains several multimedia 
    streams.
    """
    def __init__(self, *streams, path=None, ):
        if path is not None:
            self._init(path)
        else:
            self._raw = {}
            self.chapters = ()
            self.streams = []
            self.metadata = {}
            self._raw["default_filename"] = self._raw["filename"] = self._raw.get("filename")
    
        self.streams += [s for s in streams]
    
    def __repr__(self):
        path = self.path
        size = self.human_size
        duration = self.human_duration
        return f"Container(path={path}, size={size}, duration={duration})"

    def _init(self, path):
        from ._utils import call_chapters, call_format, call_streams, make_stream
        self._raw = call_format(path)
        self.chapters = tuple(call_chapters(path))
        self.streams = list(map(make_stream, call_streams(path)))
        self.metadata = self._raw.get("tags", {})
        for stream in self.streams:
            stream.container = self
        # defaults
        self._raw["default_filename"] = self._raw["filename"]
        
    @property
    def path(self) -> str:
        """The path to the file that is wrapped by the Container"""
        return self._raw.get("filename")
    
    @property
    def is_container(self) -> bool:
        return isinstance(self, Container)
    
    @property
    def extention(self) -> str:
        """The file extention."""
        if self.path:
            return os.path.splitext(self._raw["filename"])[-1]
        else:
            return None

    @property
    def default_extention(self) -> str:
        """The file extention."""
        if self.path:
            return os.path.splitext(self._raw["default_filename"])[-1]
        else:
            return None    
    
    @property
    def default_path(self) -> str:
        return self._raw.get("default_filename")
    
    # @property
    # def format(self):
    #     """The container format name"""
    #     return self._raw["format_name"]

    @property
    def size(self) -> int:
        """The file size in bytes"""
        if self._raw.get("size"):
            return int(self._raw["size"])
        else:
            return None
 
    @property
    def human_size(self) -> str:
        """The human-readable file size."""
        if self.size is None:
            return None
        if self.size == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(self.size, 1024)))
        p = math.pow(1024, i)
        s = round(self.size / p, 2)
        return f"{s} {size_name[i]}"
    
    @property
    def bitrate(self) -> int:
        """The number of bits processed per second"""
        if self._raw.get("bit_rate"):
            return int(self._raw["bit_rate"])
        else:
            return None

    @property
    def duration(self) -> float:
        """The duration in seconds"""
        if self._raw.get('duration'):
            return float(self._raw["duration"])
        else:
            return None
    
    @property
    def human_duration(self) -> str:
        """The human-readable duration."""
        if self.duration is None:
            return None
        minutes, seconds = divmod(self.duration, 60)
        hours, _ = divmod(minutes, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"    
    
    # @property
    # def start_time(self) -> float:
    #     return float(self._raw["start_time"])  
      
    @property
    def videos(self) -> tuple:
        """All video streams in the container"""
        return tuple([stream for stream in self.streams if stream.is_video])

    @property
    def audios(self) -> tuple:
        """All audio streams in the container"""
        return tuple([stream for stream in self.streams if stream.is_audio])

    @property
    def subtitles(self) -> tuple:
        """All subtitle streams in the container"""
        return tuple([stream for stream in self.streams if stream.is_subtitle])
    
    @path.setter
    def path(self, path: str):
        """Property setter for self.path."""
        if os.path.exists(path):
            raise ValueError(f"The path '{path}' already exists")
        else:
            self._raw['filename'] = path

    @extention.setter
    def extention(self, ext: str):
        """Property setter for self.extention."""
        if self.path is None:
            raise ValueError(f"Can't add the extention to the path: {self.path}")
        if ext in SUPPORTED_VIDEO_EXTENTIONS:
            root, _ = os.path.splitext(self.path)
            self.path = root + ext
        else:
            ValueError(f"The extention '{ext}' is not supported.")

    def remove_streams(self, function) -> None:
        """Removes streams for which function returns true""" 
        self.streams = [s for s in self.streams if not function(s)]

    # def trim(start, end, path, **settings): # TODO
    #     pass

    def _get_all_input_files(self):
        if self.default_path is not None:
            # self container + outer streams
            return [self] + [s for s in self.streams if not s.inner]
        else:
             # only outer streams
            return [s for s in self.streams if not s.inner]
    
    def save(self, **settings) -> int:
        compressor = FFmpegCompressor()
        compressor.add_input_files(*self._get_all_input_files())
        compressor.add_output_path(self.path)
        compressor.add_settings(**settings)
        response = compressor.run()
        self._init(self.path)
        return response

