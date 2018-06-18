import subprocess as sp
import os
from ._utils import (    
    FFMPEG_COMMAND,

    CONTAINERS_VCODECS, 
    CONTAINERS_ACODECS, 
    CONTAINERS_SCODECS, 
    CONTAINERS_TCODECS,

    FFMPEG_CODEC_FROM_SIGHT, 
    SIGHT_CODEC_FROM_FFMPEG,

    SUPPORTED_VIDEO_CODECS,
    SUPPORTED_AUDIO_CODECS,
    SUPPORTED_SUBTITLE_CODECS,
    IMAGES_CODECS,

    SUPPORTED_VIDEO_EXTENTIONS,
    SUPPORTED_AUDIO_EXTENTIONS,
    SUPPORTED_SUBTITLE_EXTENTIONS,
)


def codec_if_convert_to_extention(stream, extention):
    if stream.is_video:
        supported_codecs = CONTAINERS_VCODECS
        possible_extentions = SUPPORTED_VIDEO_EXTENTIONS
    elif stream.is_audio:
        supported_codecs = CONTAINERS_ACODECS
        possible_extentions = (
            SUPPORTED_VIDEO_EXTENTIONS + SUPPORTED_AUDIO_EXTENTIONS
        )
    elif stream.is_subtitle:
        supported_codecs = CONTAINERS_SCODECS
        possible_extentions = (
            SUPPORTED_VIDEO_EXTENTIONS + SUPPORTED_SUBTITLE_EXTENTIONS
        )
    for possible_extention in possible_extentions:
        if possible_extention == extention:
            if stream.codec in supported_codecs[extention]:
                return 'copy'
            else:
                return supported_codecs[extention][0]
    raise ValueError(f"Can't return codec for the extention '{extention}'")



class FFmpegCompressorError(Exception):
    pass


class FFmpegCompressor:
    def __init__(self):
        self.input_files = None
        self.settings = {}
        # one inner list for one input file
        self.input_paths = []
        self.input_commands = [] 
        
        self.output_path = None
        self.output_commands = []
        
        self.stream_commands_functions = [
            # common
            self.command_codec,
            self.command_map,
            self.command_metadata,
            # only video
            self.command_fps,
            self.command_frame_size,
            self.command_vtag,
        ]
        self.container_commands_functions = [
            self.command_metadata,
        ]
        self.global_commands_functions = [
            self.command_crf,
        ]

    @property
    def output_path_extention(self):
        return os.path.splitext(self.output_path)[-1]
    
    @property
    def command_without_output_path(self):
        cmd = []
        cmd += FFMPEG_COMMAND
        for i in range(len(self.input_paths)):
            cmd += self.input_commands[i]
            cmd += self.input_paths[i]
        cmd += self.output_commands
        # cmd += [self.output_path]
        return cmd

    def add_input_files(self, *input_files):
        self.input_files = list(input_files)

    def _generate_common_command(self):
        if self.input_files is None:
            raise FFmpegCompressorError(
                'FFmpegCompressor requires input files.'
            )
        for input_file in self.input_files:
            self.input_paths.append(
                ['-i', input_file.default_path]
            )
            self.input_commands.append(
                list(self._generate_input_commands(input_file))
            )
            self.output_commands.extend(
                list(self._generate_output_commands(input_file))
            )
        return self.command_without_output_path
    
    def _generate_command_for_extracting_stream(self, stream):
        if self.input_files is None:
            raise FFmpegCompressorError(
                'FFmpegCompressor requires input files.'
            )
        if len(self.input_files) > 1:
            raise FFmpegCompressorError(
                f'To select a stream you need one input file, but received \
                {len(self.input_files)}'
            )
        container = self.input_files[0]

        self.input_paths.append(['-i', container.default_path])
        self.input_commands.append(
                list(self._generate_input_commands(container))
            )
        self.output_commands.extend(
                list(self._generate_output_commands(stream))
            )
        return self.command_without_output_path

    def add_output_path(self, path):
        self.output_path = path
    
    def add_settings(self, **settings):
        self.settings = settings

    def _run_command(self, command, temp_output_path):
        command.append(temp_output_path)
        print(command)
        response = sp.run(command)
        if response:
            self._remove_and_rename_path(temp_output_path, self.output_path)
        return response

    def run(self):
        self._run_command(
            self._generate_common_command(),
            self._choose_temp_path(self.output_path)
            )

    def extract_stream_run(self, stream):
        self._run_command(
            self._generate_command_for_extracting_stream(stream),
            self._choose_temp_path(self.output_path)
            )
    
    def _remove_and_rename_path(self, temp_path, path):
        if temp_path != path:
            os.remove(path)
            os.rename(temp_path, path)    
    
    def _choose_temp_path(self, default_path):
        if not os.path.exists(default_path):
            return default_path
        i = 1
        root, ext = os.path.splitext(default_path)
        temp_path = f"{root} (temp {i}){ext}"
        while os.path.exists(temp_path):
            i += 1
            temp_path = f"{root} (temp {i}){ext}"
        return temp_path
    
    def _generate_input_commands(self, input_file):
        commands = []
        if input_file.is_container and input_file.default_extention == '.avi':
            commands += ['-fflags', '+genpts']
        return commands

    def _generate_output_commands(self, input_file):
        if input_file.is_container:
            streams = [s for s in input_file.streams if s.inner]
            container = input_file
        else:
            streams = [input_file]
            container = None
        # stream commands
        for command_function in self.stream_commands_functions:
            for stream in streams:
                yield from command_function(stream)
        # container commands
        if container:
            for command_function in self.container_commands_functions:
                yield from command_function(container)
        # global container commands
            for command_function in self.global_commands_functions:
                yield from command_function()

    # COMMANDS

    def command_codec(self, x):
        if x.is_attachment:
            return []
        extention = self._get_output_extention()
        option = f"-{x.type[0]}codec:{x.index}" 
        argument = FFMPEG_CODEC_FROM_SIGHT.get(
            codec_if_convert_to_extention(x, extention), 
            codec_if_convert_to_extention(x, extention)
        )
        if x.is_video and (x.with_changed_fps() or x.with_changed_frame_size()):
            argument = FFMPEG_CODEC_FROM_SIGHT.get(x.codec, x.codec)
        return [option, argument]

    def command_map(self, x):
        if x.is_attachment and not self._keep_attachment(x):
            return []
        i_s_i = self._get_input_specifier_index_for(x)
        return ["-map", f"{i_s_i}:{x.index}"]
    
    def command_metadata(self, x):
        if not x.is_container:
            if x.is_attachment and not self._keep_attachment(x):
                return []
            o_s_i = f':s:{self._get_output_specifier_index_for(x)}'
        else:
            o_s_i = ''
        result = []
        for key, value in x.metadata.items():
            result += [f"-metadata{o_s_i}", f"{key}={value}"]
        return result
    
    def command_fps(self, x):
        if not x.is_video:
            return []
        i_s_i = self._get_input_specifier_index_for(x)
        if x.with_changed_fps():
            return [f"-r:{i_s_i}:{x.index}", x.fps]
        else:
            return []
    
    def command_frame_size(self, x):
        if not x.is_video:
            return []
        i_s_i = self._get_input_specifier_index_for(x)
        if x.with_changed_frame_size():
            return [f'-s:{i_s_i}:{x.index}', f"{x.width}x{x.height}"]
        else:
            return []
    
    def command_crf(self):
        if self.settings.get('crf'):
            return ['-crf', self.settings['crf']]
        else:
            return []
    
    def command_vtag(self, x):
        if not x.is_video:
            return []
        extention = self._get_output_extention()
        codec = FFMPEG_CODEC_FROM_SIGHT.get(
            codec_if_convert_to_extention(x, extention), 
            codec_if_convert_to_extention(x, extention)
        )
        if codec == 'copy':
            codec = FFMPEG_CODEC_FROM_SIGHT.get(
                x.codec, 
                x.codec
            )
        is_m4v_or_mp4 = (extention == '.m4v' or extention == '.mp4')
        is_hevc = codec in ['libx265', 'hevc']
        if is_hevc and is_m4v_or_mp4:
            return ['-vtag', 'hvc1'] 
        else:
            return []
     
    def _get_output_specifier_index_for(self, x):
        o = 0
        for input_file in self.input_files:
            if input_file.is_container:
                for stream in input_file.streams:
                    if x == stream:
                        return o
                    o += 1
            else:
                if x == input_file:
                    return o
                o += 1

    def _get_input_specifier_index_for(self, x):
        for i, input_file in enumerate(self.input_files):
            if input_file.is_container:
                for stream in filter(lambda x: x.container is input_file, input_file.streams):
                    if x == stream:
                        return i
            else:
                if x == input_file:
                    return i
    
    def _get_output_extention(self):
        return os.path.splitext(self.output_path)[-1]

    def _keep_attachment(self, x):
        for c in (c for c in self.input_files if c.is_container):
            if c.streams.index(x):
                if c.default_extention == self.output_path_extention:
                    return True



