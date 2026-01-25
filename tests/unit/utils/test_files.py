# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import tempfile
from pathlib import Path

from fastdistill.utils.files import list_files_in_dir


def test_list_files_in_dir() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        created_files = []
        for i in range(20):
            file_path = temp_dir / f"{i}.txt"
            created_files.append(file_path)
            with open(file_path, "w") as f:
                f.write("hello")

        assert list_files_in_dir(Path(temp_dir)) == created_files
