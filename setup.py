import re
import sys
from setuptools import setup, find_packages

assert sys.version_info >= (3, 6, 0), 'shane requires Python 3.6+'
from pathlib import Path


BASE = Path(__file__).parent
NAME = 'shane'


def get_long_description() -> str:
    with open(BASE / 'README.md', 'r', encoding='utf-8') as f:
        return f.read()


def get_version() -> str:
    with open(BASE / NAME / '__version__.py', 'r', encoding='utf-8') as f:
        match = re.search(r'__version__\s+=\s+(?P<version>.*)', f.read())
        version = match.group('version')
        return eval(version)


setup(
    name=NAME,
    version=get_version(),
    description= 'A simple way to manage video files.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Dima Koskin',
    author_email='dmksknn@gmail.com',
    python_requires='>=3.6',
    url='https://github.com/dmkskn/shane',
    packages=find_packages(),
    license='MIT',
    keywords='video metadata converting muxing ffmpeg',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
    ],
    )
