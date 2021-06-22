import core.utils as utils

class Video:
    def __init__(self, filename):
        raw_metadata = utils.get_file_metadata(filename)
        self._metadata = utils.cleanup_metadata(filename, raw_metadata)

    def get_metadata(self):
        return self._metadata
