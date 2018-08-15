import unittest
from pathlib import Path

from mabuse.ffmpeg import FFprobe


BASE = Path(__file__).parent
SAMPLES = BASE / "samples"
CONTAINERS_DIR = SAMPLES / "containers"


class TestFFprobe(unittest.TestCase):
    def setUp(self):
        path = CONTAINERS_DIR / "mkv_container.mkv"
        self.ffprobe = FFprobe(path)

    def test_get_all_keys(self):
        d = self.ffprobe.get_all()
        self.assertTrue(isinstance(d, dict))
        self.assertIn("streams", d)
        self.assertIn("chapters", d)
        self.assertIn("format", d)

    def test_getting_streams(self):
        d = self.ffprobe.get_streams()
        self.assertTrue(isinstance(d, list))
        self.assertTrue(isinstance(d[0], dict))

    def test_getting_chapters(self):
        d = self.ffprobe.get_chapters()
        self.assertTrue(isinstance(d, list))

    def test_getting_format(self):
        d = self.ffprobe.get_format()
        self.assertTrue(isinstance(d, dict))


if __name__ == "__main__":
    unittest.main()

