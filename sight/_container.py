import os
import math
from pathlib import Path
import subprocess as sp
from ._utils import ffmpeg_command

class Container:
    """A Container wraps a file that contains several multimedia 
    streams.
    """
    def __init__(self, format_, chapters, streams):
        self._raw = format_
        self.chapters = chapters
        self.streams = streams
        self.metadata = self._raw.get("tags", {})

        # defaults
        self._raw["default_filename"] = self._raw["filename"]
        
        for stream in self.streams:
            stream.container = self
    
    def __repr__(self):
        path = self.path
        size = self.human_size
        duration = self.human_duration
        return f"Container(path={path}, size={size}, duration={duration})"
    
    @property
    def path(self) -> str:
        """The path to the file that is wrapped by the Container"""
        return self._raw["filename"]
    
    @property
    def extention(self) -> str:
        """The file extention."""
        return str(Path(self._raw["filename"]).suffix)
    
    @property
    def _default_path(self) -> str:
        return self._raw["default_filename"]
    
    @property
    def format(self):
        """The container format name"""
        return self._raw["format_name"]

    @property
    def size(self) -> int:
        """The file size in bytes"""
        return int(self._raw["size"])
    
    @property
    def human_size(self) -> str:
        """The human-readable file size."""
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
        return int(self._raw["bit_rate"])

    @property
    def duration(self) -> float:
        """The duration in seconds"""
        return float(self._raw["duration"])
    
    @property
    def human_duration(self) -> str:
        """The human-readable duration."""
        minutes, seconds = divmod(self.duration, 60)
        hours, _ = divmod(minutes, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"    
    
    @property
    def start_time(self) -> float:
        return float(self._raw["start_time"])  
      
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
        if os.path.exists(path):
            raise ValueError(f"The path '{path}' is already exists")
        else:
            self._raw['filename'] = path

    def remove_stream(self, function) -> None:
        """Removes streams for which function returns true""" 
        self.streams = [s for s in self.streams if not function(s)]
    
    def save(self) -> int:
        """Saves all changes"""
        def _generate_input_paths(inputs):
            return [input_file._raw["default_filename"] for input_file in inputs]

        def _generate_input_options(inputs):
            result = []
            for x in inputs:
                if isinstance(x, Container):
                    result += [[]]
                else:
                    # streams from another container or outer streams
                    if x._codec_if_convert_to[self.extention] == "copy":
                        result += [[]]
                    else:
                        result += [
                            [   # -[v|a|s|d]codec copy|option
                                f"-{x.codec_type[0]}codec",
                                x._codec_if_convert_to[self.extention],
                            ]
                        ]
            return result

        def _input_paths_and_their_options(inputs):
            result = []
            input_options = _generate_input_options(inputs)
            input_paths = _generate_input_paths(inputs)
            for options, path in zip(input_options, input_paths):
                result += options  # options are list
                result += ["-i", path]
            return result

        def _generate_output_options(inputs):
            commands = []
            commands += _add_metadata(self, "")  # global metadata
            o = 0  # output specifier index
            for i, inpt in enumerate(inputs):  # i is input specifier
                # every inpt is an object:
                # - 'self' Container
                # - 'other' Container's Stream
                # - 'outer' Stream
                if isinstance(inpt, Container) and inpt is not self:
                    raise EOFError  # TODO Error
                if inpt is self:  # inpt is 'self' Contaier
                    for stream in filter(lambda x: x.container is self, inpt.streams):
                        commands += stream._make_output_commands(i, o, self.extention)
                else:  # inpt is 'other' Container's Stream OR 'outer' Stream
                    commands += inpt._make_output_commands(i, o, self.extention)
                o += 1
            return commands

        def _add_metadata(x, output_specifier):
            result = []
            for key, value in x.metadata.items():
                result += [f"-metadata{output_specifier}", f"{key}={value}"]
            return result

        def _choose_temp_path(default_path):
            i = 1
            root, ext = os.path.splitext(default_path)
            temp_path = f"{root} (temp {i}){ext}"
            while os.path.exists(temp_path):
                i += 1
                temp_path = f"{root} (temp {i}){ext}"
            return temp_path
            
        inputs = [self] + [s for s in self.streams if not s.inner]
        call = []
        call += ffmpeg_command
        call += _input_paths_and_their_options(inputs)
        call += _generate_output_options(inputs)

        # if path was not changed
        if self.path == self._default_path:
            path = _choose_temp_path(self.path)
        else:
            path = self.path
        
        call += [path]
        # print(call)
        response = sp.call(call)

        if self.path == self._default_path:
            temp = self.path
            os.remove(self.path)
            os.rename(path, temp)

        return response
