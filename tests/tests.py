import inspect
import sys
import unittest
from pathlib import Path

import shane

BASE = Path(__file__).parent
SAMPLES = BASE / "examples"
BASE = Path(__file__).parent
SAMPLES = BASE / "samples"
CONTAINERS_DIR = SAMPLES / "containers"


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
    assert Path(SAMPLES / file).exists(), \
    f"Path '{Path(SAMPLES / file)}' doesn't exists."


class TestOpenFile(unittest.TestCase):
    def test_open_container(self):
        mkv = shane.open(SAMPLES / "mkv_container.mkv")
        mp4 = shane.open(SAMPLES / "mp4_container.mp4")
        avi = shane.open(SAMPLES / "avi_container.avi")

        self.assertIsInstance(mkv, shane._container.Container)
        self.assertIsInstance(mp4, shane._container.Container)
        self.assertIsInstance(avi, shane._container.Container)

    def test_open_stream(self):
        mkv = shane.open(SAMPLES / "mkv_stream.mkv")
        avi = shane.open(SAMPLES / "avi_stream.avi")
        mp4 = shane.open(SAMPLES / "mp4_stream.mp4")
        aac = shane.open(SAMPLES / "aac_stream.aac")
        ac3 = shane.open(SAMPLES / "ac3_stream.ac3")
        srt = shane.open(SAMPLES / "srt_stream.srt")

        self.assertIsInstance(mkv, shane._streams.VideoStream)
        self.assertIsInstance(avi, shane._streams.VideoStream)
        self.assertIsInstance(mp4, shane._streams.VideoStream)
        self.assertIsInstance(aac, shane._streams.AudioStream)
        self.assertIsInstance(ac3, shane._streams.AudioStream)
        self.assertIsInstance(srt, shane._streams.SubtitleStream)


class TestContainer(unittest.TestCase):
    def setUp(self):
        mkv = shane.open(SAMPLES / "mkv_container.mkv")
        mp4 = shane.open(SAMPLES / "mp4_container.mp4")
        avi = shane.open(SAMPLES / "avi_container.avi")

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
        mkv = shane.open(SAMPLES / "mkv_stream.mkv")
        avi = shane.open(SAMPLES / "avi_stream.avi")
        mp4 = shane.open(SAMPLES / "mp4_stream.mp4")
        # plus inner streams


class TestAudioStream(TestStream):
    def setUp(self):
        aac = shane.open(SAMPLES / "aac_stream.aac")
        ac3 = shane.open(SAMPLES / "ac3_stream.ac3")
        # plus inner streams

class TestSubtitleStream(TestStream):
    def setUp(self):
        srt = shane.open(SAMPLES / "srt_stream.srt")
        # plus inner stream


if __name__ == "__main__":
    unittest.main()