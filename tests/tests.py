import inspect
import sys
import unittest
from pathlib import Path

import sight

BASE = Path(__file__).parent
EXAMPLES = BASE / "examples"


FILES_FOR_TESTS = [
    # containers:
    "mkv_container.mkv",
    "mp4_container.mp4",
    "avi_container.avi",
    # video streams (containers with only one stream):
    "mkv_stream.mkv",
    "avi_stream.avi",
    "mp4_stream.mp4",
    # audio streams:
    "aac_stream.aac",
    "ac3_stream.ac3",
    # subtitle streams:
    "srt_stream.srt",
]
for file in FILES_FOR_TESTS:
    assert Path(EXAMPLES / file).exists(), \
    f"Path '{Path(EXAMPLES / file)}' doesn't exists."


class TestOpenFile(unittest.TestCase):
    def test_open_container(self):
        mkv = sight.open(EXAMPLES / "mkv_container.mkv")
        mp4 = sight.open(EXAMPLES / "mp4_container.mp4")
        avi = sight.open(EXAMPLES / "avi_container.avi")

        self.assertIsInstance(mkv, sight._container.Container)
        self.assertIsInstance(mp4, sight._container.Container)
        self.assertIsInstance(avi, sight._container.Container)

    def test_open_stream(self):
        mkv = sight.open(EXAMPLES / "mkv_stream.mkv")
        avi = sight.open(EXAMPLES / "avi_stream.avi")
        mp4 = sight.open(EXAMPLES / "mp4_stream.mp4")
        aac = sight.open(EXAMPLES / "aac_stream.aac")
        ac3 = sight.open(EXAMPLES / "ac3_stream.ac3")
        srt = sight.open(EXAMPLES / "srt_stream.srt")

        self.assertIsInstance(mkv, sight._streams.VideoStream)
        self.assertIsInstance(avi, sight._streams.VideoStream)
        self.assertIsInstance(mp4, sight._streams.VideoStream)
        self.assertIsInstance(aac, sight._streams.AudioStream)
        self.assertIsInstance(ac3, sight._streams.AudioStream)
        self.assertIsInstance(srt, sight._streams.SubtitleStream)


class TestContainer(unittest.TestCase):
    def setUp(self):
        mkv = sight.open(EXAMPLES / "mkv_container.mkv")
        mp4 = sight.open(EXAMPLES / "mp4_container.mp4")
        avi = sight.open(EXAMPLES / "avi_container.avi")

    def test_ability_to_change_values(self):
        self.fail(f"Write {inspect.stack()[0][3]}")

    def test_ban_on_changing_default_values(self):
        self.fail(f"Write {inspect.stack()[0][3]}")

    def test_adding_new_streams(self):
        self.fail(f"Write {inspect.stack()[0][3]}")

    def test_removing_streams(self):
        self.fail(f"Write {inspect.stack()[0][3]}")


class TestStream(unittest.TestCase): # Base
    def test_ability_to_change_values(self):
        self.fail(f"Write {inspect.stack()[0][3]}")

    def test_ban_on_changing_default_values(self):
        self.fail(f"Write {inspect.stack()[0][3]}")
    
    def test_check_container_of_stream(self):
        self.fail(f"Write {inspect.stack()[0][3]}")
    
    def test_extract_stream_from_container(self):
        self.fail(f"Write {inspect.stack()[0][3]}")
    
    def test_save_outer_stream(self):
        self.fail(f"Write {inspect.stack()[0][3]}")
    

class TestVideoStream(TestStream):
    def setUp(self):
        mkv = sight.open(EXAMPLES / "mkv_stream.mkv")
        avi = sight.open(EXAMPLES / "avi_stream.avi")
        mp4 = sight.open(EXAMPLES / "mp4_stream.mp4")
        # plus inner streams


class TestAudioStream(TestStream):
    def setUp(self):
        aac = sight.open(EXAMPLES / "aac_stream.aac")
        ac3 = sight.open(EXAMPLES / "ac3_stream.ac3")
        # plus inner streams

class TestSubtitleStream(TestStream):
    def setUp(self):
        srt = sight.open(EXAMPLES / "srt_stream.srt")
        # plus inner stream
