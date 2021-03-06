import os
from ._utils import Something


__all__ = ['open']


def open(path):
    if not os.path.exists(path):
        raise FileNotFoundError("The path '{path}' doesn't exists.")
    else:
        something = Something(path)
    
    if something.is_stream:
        return something.as_stream()
    else:
        return something.as_container()
