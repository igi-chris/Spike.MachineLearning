import os
import re
import unicodedata

from literals import base_dir, tmp_files_dir_name, training_data_fname


def ref_from_path(path: str) -> str:
    pattern = "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
    regex = re.compile(pattern, re.I)
    res = regex.match(path)
    if res is None:
        raise ValueError(f"Unable to find GUID in path: {path}")
    return res.group(1)


def csv_path_from_ref(ref: str) -> str:
    tmp_files_dir = os.path.join(base_dir, tmp_files_dir_name)
    os.makedirs(tmp_files_dir, exist_ok=True)
    target_dir = os.path.join(tmp_files_dir, ref)
    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, training_data_fname)


def secure_filename(filename: str) -> str:
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """    
    _filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )

    return filename