"""
File Manager
"""

import re
import os.path

import yaml

from libs.misc import file_extension_regex, duplicates
from libs.file import FolderStructure

import logging
log = logging.getLogger(__name__)


AUDIO_EXTS = ('mp2', 'ogg', 'mp3', 'flac')
VIDEO_EXTS = ('avi', 'mpg', 'mkv', 'rm', 'ogm', 'mp4')
DATA_EXTS = ('yml', 'yaml')
OTHER_EXTS = ('srt', 'ssa', 'txt')

ALL_EXTS = AUDIO_EXTS + VIDEO_EXTS + DATA_EXTS + OTHER_EXTS

# Higher the index of the extension, the higher the file is ranked for processing.
# The highest ranked file of a set of names in processed
PRIMARY_FILE_RANKED_EXTS = AUDIO_EXTS + VIDEO_EXTS + DATA_EXTS

# Protection for legacy processed files  (could be removed in once data fully migriated)
DEFAULT_IGNORE_FILE_REGEX = re.compile(r'0\.mp4|0_generic\.mp4|\.bak|^\.|^0_video\.')


# Scan -------------------------------------------------------------------------

def scan_file_collections(path):
    """
    1.) Locate primary files
    2.) Group file collection (based on primary file)
    """
    folder_structure = FolderStructure.factory(
        path,
        file_regex=file_extension_regex(ALL_EXTS),
        ignore_regex=DEFAULT_IGNORE_FILE_REGEX
    )
    return {
        f.file_no_ext: _get_file_collection(folder_structure, f)
        for f in _locate_primary_files(folder_structure, file_regex=file_extension_regex(PRIMARY_FILE_RANKED_EXTS))
    }


# Scan sections ----------------------------------------------------------------

def _locate_primary_files(folder_structure, file_regex):
    """
    Locate primary files
    """
    ignore_files = set()
    file_dict = {}
    for f in folder_structure.scan(file_regex=file_regex):
        if f.file_no_ext in ignore_files:
            continue
        existing = file_dict.get(f.file_no_ext)
        if PRIMARY_FILE_RANKED_EXTS.index(f.ext) >= (PRIMARY_FILE_RANKED_EXTS.index(existing.ext) if existing else 0):
            if existing and existing.file == f.file:
                del file_dict[f.file_no_ext]
                ignore_files.add(f.file_no_ext)
                log.warn("Multiple primary files detected: Refusing to process %s %s", f.absolute, existing.absolute)
            else:
                file_dict[f.file_no_ext] = f
    return file_dict.values()


def _get_file_collection(folder_structure, primary_file):
    """
    Collect realated files
    """
    folder = folder_structure.get(primary_file.folder)

    # File collection always contains the primary file
    file_collection = set()  # {primary_file, }  # This could be uneeded as the file is added below as well

    # Collect files the same name
    file_collection |= {f for f in folder.files if f.file_no_ext == primary_file.file_no_ext}

    # Data files contain pointers to additional files that may not be named the same
    # We need to lookup the FileScan item from the in memory file list
    if primary_file.ext in DATA_EXTS:
        file_collection |= {
            folder_structure.get(os.path.join(primary_file.folder, data_filename))
            for data_filename in _load_yaml(primary_file.absolute)
        }

    # Get tags.txt from differnt folder if importing legacy files
    if folder.name == 'source' and folder.parent and folder.parent.get('tags.txt'):
        file_collection.add(folder.parent.get('tags.txt'))

    return file_collection


# Utils ------------------------------------------------------------------------

def _load_yaml(filename):
    with open(filename, 'rb') as file_handle:
        return yaml.load(file_handle)
