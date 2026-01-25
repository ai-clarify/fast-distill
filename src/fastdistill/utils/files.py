# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from pathlib import Path
from typing import Callable, List, Optional


def list_files_in_dir(
    dir_path: Path, key: Optional[Callable] = lambda x: int(x.stem)
) -> List[Path]:
    """List all files in a directory.

    Args:
        dir_path: Path to the directory.
        key: A function to sort the files. Defaults to sorting by the integer value of the file name.
            This is useful when loading files from the cache, as the name will be numbered.

    Returns:
        A list of file names in the directory.
    """
    return [f for f in sorted(dir_path.iterdir(), key=key) if f.is_file()]
