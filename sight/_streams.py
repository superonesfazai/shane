import os
import subprocess as sp
from ._utils import Something

from ._ffmpeg import FFmpegCompressor
# from ._utils import CONTAINERS_VCODECS, CONTAINERS_ACODECS, CONTAINERS_SCODECS
# from ._utils import FFMPEG_CODEC_FROM_SIGHT, SIGHT_CODEC_FROM_FFMPEG
from ._utils import (
#     SUPPORTED_VIDEO_CODECS,
#     SUPPORTED_AUDIO_CODECS,
#     SUPPORTED_SUBTITLE_CODECS,
    IMAGES_CODECS,
)
from ._utils import (
    SUPPORTED_VIDEO_EXTENTIONS,
    SUPPORTED_AUDIO_EXTENTIONS,
    SUPPORTED_SUBTITLE_EXTENTIONS,
)
# from ._utils import FFMPEG_COMMAND
# from ._utils import Something
from ._utils import SIGHT_CODEC_FROM_FFMPEG
# _fs = '-s' # frame size
# _fps = '-r'
# _map = '-map'
# _crf = '-crf'
# _codec = '-c'
# _vtag = '-vtag'

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

    # @property
    # def _codec_if_convert_to(self):
    #     if self.is_video:
    #         supported_codecs_for = CONTAINERS_VCODECS
    #         possible_extenions = SUPPORTED_VIDEO_EXTENTIONS
    #     elif self.is_audio:
    #         supported_codecs_for = CONTAINERS_ACODECS
    #         possible_extenions = (
    #             SUPPORTED_VIDEO_EXTENTIONS + SUPPORTED_AUDIO_EXTENTIONS
    #         )
    #     elif self.is_subtitle:
    #         supported_codecs_for = CONTAINERS_SCODECS
    #         possible_extenions = (
    #             SUPPORTED_VIDEO_EXTENTIONS + SUPPORTED_SUBTITLE_EXTENTIONS
    #         )
    #     else:
    #         raise NotImplementedError
    #     result = {}
    #     for extention in possible_extenions:
    #         if self.codec in supported_codecs_for[extention]:
    #             if self.codec != self._default_codec:
    #                 result[extention] = FFMPEG_CODEC_FROM_SIGHT.get(
    #                     self.codec, self.codec)
    #             else:
    #                 result[extention] = 'copy'
    #         else:
    #             codec = supported_codecs_for[extention][0]
    #             result[extention] = FFMPEG_CODEC_FROM_SIGHT.get(codec, codec)
    #     return result

    # def _map_cmd(self, **kwargs):
    #     i_s = kwargs.get('input_specifier_index')
    #     return ["-map", f"{i_s}:{self.index}"]

    # def _metadata_cmd(self, **kwargs):
    #     o_s = kwargs.get('output_specifier_index')
    #     result = []
    #     for key, value in self.metadata.items():
    #         result += [f"-metadata:s:{o_s}", f"{key}={value}"]
    #     return result

    # def _make_input_commands(self, extention):
    #     pass

    # def _make_output_commands(self, i_s, o_s, extention, **settings):
        # pass

    # def save(self):
    #     """Saves all the changes. Only for outer streams"""
    #     crf = settings.get('crf')
        
    #     def _choose_temp_path(default_path):
    #         i = 1
    #         root, ext = os.path.splitext(default_path)
    #         temp_path = f"{root} (temp {i}){ext}"
    #         while os.path.exists(temp_path):
    #             i += 1
    #             temp_path = f"{root} (temp {i}){ext}"
    #         return temp_path

    #     if self.inner:
    #         raise RuntimeError # TODO Error

    #     ext = os.path.splitext(path)[1] or self.extention
        
    #     call = []
    #     call += FFMPEG_COMMAND
    #     call += ['-i', self.default_path]
    #     call += self._make_output_commands(0, 0, ext, crf=None, to_container=False)
        
    #     if self.default_path == self.path:
    #         path = _choose_temp_path(self.default_path)
    #     else:
    #         path = self.path

    #     call += [path]
        
    #     # print(call)
    #     response = sp.call(call)

    #     if self.default_path == self.path:
    #         temp = self.default_path
    #         os.remove(self.default_path)
    #         os.rename(path, temp)
    #         path = temp
    #     self._init(path)
    #     return response
        
    # def extract(self, path=None, **settings):
    #     """Extreacts the stream and saves it to the `path`. Returns 
    #     the extracted stream"""
    #     crf = settings.get('crf')
        
    #     def _choose_temp_path(default_path):
    #         i = 1
    #         root, ext = os.path.splitext(default_path)
    #         temp_path = f"{root} (temp {i}){ext}"
    #         while os.path.exists(temp_path):
    #             i += 1
    #             temp_path = f"{root} (temp {i}){ext}"
    #         return temp_path

    #     if os.path.exists(path):
    #         raise ValueError # TODO
    #     if self.container:
    #         input_path = self.container.path 
    #     else:
    #         input_path = self.default_path
        
    #     output_path = path or self.path
        
    #     if input_path == output_path:
    #         raise ValueError # TODO Error

    #     ext = os.path.splitext(path)[1] or self.extention
        
    #     call = []
    #     call += FFMPEG_COMMAND
    #     call += ['-i', input_path]
    #     call += self._make_output_commands(0, 0, ext, crf=None, to_container=False)
    #     call += [path]
        
    #     # print(call)
    #     response = sp.call(call)
        # if response: 
        #     return response
        # something = Something(path)
        # return something.as_stream()

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
    
    # def _with_changed_fps(self):
    def with_changed_fps(self):
        return self._raw["default_avg_frame_rate"] != self._raw["avg_frame_rate"]

    # def _with_changed_frame_size(self):
    def with_changed_frame_size(self):
        return (
            self._raw["default_height"] != self._raw["height"]
            or self._raw["default_width"] != self._raw["width"]
        )

    # def _codec_cmd(self, **kwargs):
    #     i_s = kwargs.get('input_specifier_index')
    #     extention = kwargs.get('extention')
    #     input_cmd = True if i_s is None else False
    #     codec = f"-{self.type[0]}codec"
    #     # codec = f"{_codec}:{self.type[0]}"
    #     if input_cmd:
    #         self._commands_history.add(codec)
    #     else:
    #         if codec in self._commands_history:
    #             return []
    #     index = '' if input_cmd else f':{self.index}'
    #     cmd = [
    #         f'{codec}{index}',
    #         FFMPEG_CODEC_FROM_SIGHT.get(
    #             self._codec_if_convert_to[extention], 
    #             self._codec_if_convert_to[extention]
    #         )
    #     ]
    #     if cmd[1] == 'copy':
    #         if input_cmd:
    #             cmd = []
    #         elif self._with_changed_fps() or self._with_changed_frame_size():
    #             cmd[1] = FFMPEG_CODEC_FROM_SIGHT.get(self.codec, self.codec)
    #     return cmd

    # def _fps_cmd(self, **kwargs):
    #     i_s = kwargs.get('input_specifier_index')
    #     extention = kwargs.get('extention')

    #     input_cmd = True if i_s is None else False
    #     if input_cmd:
    #         self._commands_history.add(_codec)
    #     else:
    #         if _fps in self._commands_history: 
    #             return []      
    #     option = _fps if input_cmd else f"{_fps}:{i_s}:{self.index}"
    #     if self._with_changed_fps():
    #         cmd = [option, str(self.fps)]
    #         return cmd
    #     return []

    # def _frame_size_cmd(self, **kwargs):
    #     i_s = kwargs.get('input_specifier_index')
    #     extention = kwargs.get('extention')

    #     input_cmd = True if i_s is None else False
    #     if input_cmd:
    #         self._commands_history.add(_codec)
    #     else:
    #         if _fs in self._commands_history: 
    #             return []  
    #     option = _fs if input_cmd else f'{_fs}:{i_s}:{self.index}'
    #     if self._with_changed_frame_size():
    #         cmd = [option, f"{self.width}x{self.height}"]
    #         return cmd
    #     else:
    #         return []

    # def _crf_cmd(self, **kwargs):
    #     if _crf in self._commands_history: 
    #         return []  
    #     else:
    #         self._commands_history.add(_crf)
        
    #     if kwargs.get('crf'):
    #         return [_crf, kwargs['crg']]
    #     else:
    #         return []

    # def _vtag_cmd(self, **kwargs):
    #     if _vtag in self._commands_history: 
    #         return []  
    #     else:
    #         self._commands_history.add(_vtag)
    #     extention = kwargs.get('extention')
    #     codec = FFMPEG_CODEC_FROM_SIGHT.get(
    #         self._codec_if_convert_to[extention], 
    #         self._codec_if_convert_to[extention]
    #     )
    #     if codec == 'copy':
    #         codec = FFMPEG_CODEC_FROM_SIGHT.get(
    #             self.codec, 
    #             self.codec
    #         )
    #     is_m4v_or_mp4 = (extention == '.m4v' or extention == '.mp4')
    #     is_hevc = (codec == 'libx265' or codec == 'hevc')
    #     if is_hevc and is_m4v_or_mp4:
    #         return [_vtag, 'hvc1'] 
    #     else:
    #         return []

    # def _make_input_commands(self, extention):
    #     commands_functions = [

    #     ]
    #     kwargs = {
    #         'extention': extention,
    #     }
    #     commands = []
    #     for func in commands_functions:
    #         commands += func(**kwargs)
    #     return commands 

    # def _make_output_commands(self, i_s, o_s, extention, **settings):
    #     commands_functions = [
    #         self._codec_cmd, 
    #         self._fps_cmd, 
    #         self._frame_size_cmd,
    #         self._crf_cmd,
    #         self._vtag_cmd,
    #         self._map_cmd,
    #         self._metadata_cmd,
    #     ]
    #     commands = []
    #     kwargs = {
    #         'input_specifier_index': i_s,
    #         'output_specifier_index': o_s,
    #         'extention': extention,
    #         'crf': settings.get('crf'),
    #     }
    #     for func in commands_functions:
    #         commands += func(**kwargs)
    #     return commands 

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

    # @property
    # def bitrate(self) -> int:
    #     """The number of bits processed per second."""
    #     return int(self._raw["bit_rate"])

    # @bitrate.setter
    # def bitrate(self, value: int):
    #     """Property setter for self.height."""
    #     if isinstance(value, int):
    #         self._raw["bit_rate"] = value
    #     else:
    #         raise TypeError("The bitrate value must be an integer.")

    # TODO @sample_rate.setter
    # TODO @channels.setter

    # def _codec_cmd(self, **kwargs):
    #     i_s = kwargs.get('input_specifier_index')
    #     extention = kwargs.get('extention')
    #     input_cmd = True if i_s is None else False
    #     # codec = f"{_codec}:{self.type[0]}"
    #     codec = f"-{self.type[0]}codec"
    #     if input_cmd:
    #         self._commands_history.add(codec)
    #     else:
    #         if codec in self._commands_history:
    #             return []
    #     index = '' if input_cmd else f':{self.index}'
    #     cmd = [
    #         f'{codec}{index}',
    #         FFMPEG_CODEC_FROM_SIGHT.get(
    #             self._codec_if_convert_to[extention], 
    #             self._codec_if_convert_to[extention]
    #         )
    #     ]
    #     if input_cmd and cmd[1] == 'copy':
    #         cmd = []
    #     return cmd
    
    # def _make_input_commands(self, extention):
    #     commands_functions = [

    #     ]
    #     kwargs = {
    #         'extention': extention,
    #     }
    #     commands = []
    #     for func in commands_functions:
    #         commands += func(**kwargs)
    #     return commands 

    # def _make_output_commands(self, i_s, o_s, extention, **settings):
    #     commands_functions = [
    #         self._codec_cmd, 
    #         self._map_cmd,
    #         self._metadata_cmd,
    #     ]
    #     commands = []
    #     kwargs = {
    #         'input_specifier_index': i_s,
    #         'output_specifier_index': o_s,
    #         'extention': extention,
    #         'crf': settings.get('crf'),
    #     }
    #     for func in commands_functions:
    #         commands += func(**kwargs)
    #     return commands 

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

    # def _codec_cmd(self, **kwargs):
    #     i_s = kwargs.get('input_specifier_index')
    #     extention = kwargs.get('extention')
    #     input_cmd = True if i_s is None else False
    #     # codec = f"{_codec}:{self.type[0]}"
    #     codec = f"-{self.type[0]}codec"
    #     if input_cmd:
    #         self._commands_history.add(codec)
    #     else:
    #         if codec in self._commands_history:
    #             return []
    #     index = '' if input_cmd else f':{self.index}'
    #     cmd = [
    #         f'{codec}{index}',
    #         FFMPEG_CODEC_FROM_SIGHT.get(
    #             self._codec_if_convert_to[extention], 
    #             self._codec_if_convert_to[extention]
    #         )
    #     ]
    #     if input_cmd and cmd[1] == 'copy':
    #         cmd = []
    #     return cmd

    # def _make_input_commands(self, extention):
    #     commands_functions = [
    #         # self._codec_cmd, 
    #     ]
    #     kwargs = {
    #         'extention': extention,
    #     }
    #     commands = []
    #     for func in commands_functions:
    #         commands += func(**kwargs)
    #     return commands 

    # def _make_output_commands(self, i_s, o_s, extention, **settings):
    #     commands_functions = [
    #         self._codec_cmd, 
    #         self._map_cmd,
    #         self._metadata_cmd,
    #     ]
    #     commands = []
    #     kwargs = {
    #         'input_specifier_index': i_s,
    #         'output_specifier_index': o_s,
    #         'extention': extention,
    #         'crf': settings.get('crf'),
    #     }
    #     for func in commands_functions:
    #         commands += func(**kwargs)
    #     return commands  

    def __repr__(self):
        return (self.__class__.__name__ + "("
            f"path={self.path}, codec={self.codec}, is_forced={self.is_forced}, " + 
            f"language={self.metadata.get('language')}" +
            ")"
        )



class DataStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)
    
    # def _make_output_commands(self, i_s, o_s, extention, **settings):
    #     return []
        
    # def _make_input_commands(self, extention):
    #     return []



class ImageStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)

    # def _make_output_commands(self, i_s, o_s, extention, **settings):
    #     return []

    # def _make_input_commands(self, extention):
    #     return []



class AttachmentStream(Stream): # ?
    def __init__(self, raw):
        Stream.__init__(self, raw)

    # def _codec_cmd(self, **kwargs):
    #     return [f"tcodec:{self.index}", 'copy']
       
    # def _make_output_commands(self, i_s, o_s, extention, **settings):
    #     commands_functions = [
    #         self._codec_cmd, 
    #         self._map_cmd,
    #         self._metadata_cmd,
    #     ]
    #     commands = []
    #     kwargs = {
    #         'input_specifier_index': i_s,
    #         'output_specifier_index': o_s,
    #         'extention': extention,
    #         'crf': settings.get('crf'),
    #     }
    #     for func in commands_functions:
    #         commands += func(**kwargs)
    #     return commands  

    def __repr__(self):
        return (self.__class__.__name__ + "("
            f"path={self.path}, codec={self.codec}, " + 
            f"language={self.metadata.get('language')}" +
            ")"
        )

    # def _make_input_commands(self, extention):
    #     return []