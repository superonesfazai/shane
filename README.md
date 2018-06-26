

Sight is a handy module for converting and demuxing video files.

- Change a container for MKV or MP4 without slow re-encoding.
- Add new streams to the container (and delete other ones easily)
- View and change the metadata of a container and of all its streams

It is a new look at some common tasks for FFmpeg (you don't need to know FFmpeg syntax). In fact, you just change some media file attributes, like `extention` or `fps`, and save these changes (see examples below).


## CONTENTS
1. [INSTALLATION](#installation)
2. [HOW TO](#how-to)
    - [Open the media file](#open-the-media-file)
	- [Change the format to another one](#change-the-format-to-another-one)
	- [Delete all audio tracks that are not Engilsh](#delete-all-audio-tracks-that-are-not-engilsh)
	- [Add subtitles](#add-subtitles)
	- [Save the changes](#save-the-changes)
3. [USAGE](#usage)
	- [Open a file](#open-a-file)
	- [Discover the media information](#discover-the-media-information)
	- [Change what you want](#change-what-you-want)


## INSTALLATION
Install [FFmpeg](http://ffmpeg.org). You can install it using Homebrew on Mac:

```
brew install ffmpeg --with-x265
```

Install Sight with pip:
```
pip install sight
```

Note, that only **Python 3.6+** is supported.


## HOW TO

### Open the media file:
```
>>> import sight
>>> container = sight.open('path/to/file.mkv')
```

### Change the format to another one:
**NOTE:** It will be executed fast if the input container codecs are supported by the output container.
```
>>> container.extention = '.m4v'
```

### Delete all audio tracks, that are not Engilsh:
```
>>> not_eng = lambda s: s.is_audio and s.metadata['language'] != 'eng'
>>> container.remove_streams(not_eng)
```

### Add subtitles:
```
>>> subtitles = sight.open('path/to/fre_subtitles.srt')
>>> subtitles.metadata['language'] = 'fre'
>>> container.streams.append(subtitles)
```

### Extract subtitles:
```
>>> subtitles = container.subtitles[0]
>>> subtitles = subtitles.extreact(path='new_path/to/rus_subtitles.srt')
```

### Save the changes:

After all the changes, the file must be saved.

**NOTE:** If the `path` or the `extention` of a file was not changed, the file will be rewritten entirely. 
```
>>> container.save()
```

## USAGE

Sight operates with two kinds of objects: *streams* and *containers*. Streams are *separate* video/audio/subtitles files and containers contain a number of streams. 

### Open a file

The `open` function chooses the object type that needs to be created itself.

Open the file with several video/audio/subtitles tracks in it:
```
>>> container = sight.open('path/to/file.mkv')
Container(path=path/to/file.mkv, size=142.65 MB, duration=00:02:00)
```

Open the file that contains only video, without any audio or subtitles:
```
>>> video_stream = sight.open('path/to/only_video.mkv')
VideoStream(path=path/to/file.mkv, codec=h264, fps=23.97598627787307, width=1272, height=720, language=eng)
```

Open an audio or subtitles file:
```
>>> audio_stream = sight.open('path/to/audio.aac')
AudioStream(path=path/to/audio.aac, codec=aac, channels=2, sample_rate=48000.0, language=eng)

>>> subtitle_stream = sight.open('path/to/subtitles.srt')
SubtitleStream(path=path/to/subtitles.srt, codec=subrip, is_forced=False, language=rus)
```
### Discover the media information

Get the `list` of all streams inside the container:
```
>>> container.streams
...
```
Get `tuple` of streams of a certain type:
```
>>> container.audios
...
>>> container.subtitles
...
>>> container.videos
...
```
Get the metadata:
```
# global metadata
>>> container.metadata
{'title': 'Untitled Movie File'}

# metadata of a certain stream
>>> *_, last_audio_stream = container.audios
>>> last_audio_stream.metadata
{'language': 'eng', 'title': 'Commentary', 'DURATION': '00:02:00'}
```

Get chapters:
```
>>> container.chapters
...
 ```

Get other media information:
```
>>> container.path
'path/to/file.mkv'

>>> container.extention
'.mkv'

>>> container.duration
120.0

>>> container.human_duration
'00:02:00'

>>> container.size
149575198

>>> container.human_size
'142.65 MB'

>>> video, *_ = container.videos
>>> video.fps
23.976023976023978

>>> video.codec
'h264'
```

### Change what you want

All the changes to the container are performed by means of changing of its attributes and the following saving.

Change the file extention:
```
>>> container.extention = '.m4v'

>>> container.path
'path/to/file.m4v'
```

Change the global metadata:
```
>>> container.metadata['author'] = "John Dou"
```

Or delete the global metadata at all:
 ```
>>> container.metadata = {}
```

Change the FPS of the video stream inside the container:
```
>>> video_stream, *_ = container.videos
>>> video_stream.fps = 23
```

Change the frame size:
```
>>> video_stream.width = 640
>>> video_stream.height = 480
```

And don't forget to save the changes:
```
>>> container.save()
```
