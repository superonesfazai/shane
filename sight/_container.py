import os


class Container:
    """A Container wraps a file that contains several multimedia 
    streams.
    """
    def __init__(self, format_, chapters, streams):
        self._raw = format_
        self.chapters = chapters
        self.streams = streams
        self.metadata = self._raw.get("tags", {})

    @property
    def path(self):
        """The path to the file that is wrapped by the Container"""
        return self._raw["filename"]

    @property
    def format(self):
        """The container format name"""
        return self._raw["format_name"]

    @property
    def size(self):
        """The file size in bytes"""
        return int(self._raw["size"])

    @property
    def bitrate(self):
        """The number of bits processed per second"""
        return int(self._raw["bit_rate"])

    @property
    def duration(self):
        """The duration in seconds"""
        return float(self._raw["duration"])
    
    @property
    def videos(self):
        """All video streams in the container"""
        return tuple([stream for stream in self.streams if stream.is_video])

    @property
    def audios(self):
        """All audio streams in the container"""
        return tuple([stream for stream in self.streams if stream.is_audio])

    @property
    def subtitles(self):
        """All subtitle streams in the container"""
        return tuple([stream for stream in self.streams if stream.is_subtitle])
    
    @path.setter
    def path(self, path):
        if os.path.exists(path):
            raise ValueError(f"The path '{path}' is already exists")
        else:
            self._raw['filename'] = path

    def save(self): # TODO
        """Saves all changes"""
        raise NotImplementedError
