import os.path
import shutil
import hashlib
from collections import namedtuple
from libs.misc import fast_scan

ProcessedFileType = namedtuple('ProcessedFileType', ('type', 'ext', 'salt'))


class ProcessedFilesManager(object):
    DEFAULT_NUMBER_OF_IMAGES = 4
    FILE_TYPE_LOOKUP = {
        processed_file_type.type: processed_file_type
        for processed_file_type in (
            ProcessedFileType('image', 'jpg', ''),
            ProcessedFileType('video', 'mp4', ''),
            ProcessedFileType('preview', 'mp4', ''),
            ProcessedFileType('srt', 'srt', ''),
        )
    }

    def __init__(self, path):
        self.path = path

    def _factory(self, hashs, ext):
        return ProcessedFile(self.path, hashs, ext)

    def get_processed_file(self, source_hash, file_type, *args):
        file_type = self.FILE_TYPE_LOOKUP[file_type]
        return self._factory(
            (source_hash, file_type.type, file_type.salt, ''.join((str(a) for a in args))),
            file_type.ext
        )

    def get_all_processed_files_associated_with_meta(self, source_hash):
        if hasattr(source_hash, 'processed_data'):
            source_hash = source_hash.processed_data.get('main', {}).get('hash')
        if not source_hash:
            return ()
        return tuple(
            self.get_processed_file(source_hash, t)
            for t in ('video', 'preview', 'srt')
        ) + tuple(
            self.get_processed_file(source_hash, 'image', image_num)
            for image_num in range(self.DEFAULT_NUMBER_OF_IMAGES)
        )

    @property
    def scan(self):
        return fast_scan(self.path)


class ProcessedFile(object):
    def __init__(self, path, hashs, ext):
        self.hash = gen_string_hash(hashs)
        self.absolute = os.path.abspath(os.path.join(path, '{}.{}'.format(self.hash, ext)))

    def move(self, source_file):
        """
        It is important that 'move' is used rather than opening a stream to the
        absolute path directly.
        The remote destination could be 'scp' or another remote service.
        Always using move allows for this abstraction at a later date
        """
        shutil.move(source_file, self.absolute)

    @property
    def exists(self):
        return os.path.exists(self.absolute)


def gen_string_hash(hashs):
    if isinstance(hashs, str):
        hash_str = hashs
    else:
        hasher = hashlib.sha256()
        hasher.update(''.join(sorted(hashs)).encode('utf-8'))
        hash_str = hasher.hexdigest()
    return hash_str
