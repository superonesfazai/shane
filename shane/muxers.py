
def mkv(container):
    """Changes the `container` format to the MKV format."""
    container.extention = '.mkv'
    container.save()
    return container

def m4v(container):
    """Changes the `container` format to the M4V format."""
    container.extention = '.m4v'
    container.save()
    return container

