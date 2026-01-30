# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import logging
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pyarrow as pa
import pyarrow.parquet as pq

from fastdistill import envs
from fastdistill.pipeline.batch import _Batch
from fastdistill.utils.dicts import flatten_dict
from fastdistill.utils.files import list_files_in_dir


class _WriteBuffer:
    """Class in charge of sending the batched contents to a buffer and writing
    those to files under a given folder.

    As batches are received, they are added to the buffer and once each buffer
    is full, the content is written to a parquet file.
    """

    def __init__(
        self,
        path: "PathLike",
        leaf_steps: Set[str],
        steps_cached: Optional[Dict[str, bool]] = None,
        buffer_batch_size: Optional[int] = None,
    ) -> None:
        """
        Args:
            path: Folder where the files will be written, the idea
                is for this path to be in the cache folder under /data.
            leaf_steps: Leaf steps from either the DAG of the Pipeline.
            steps_cached: Dictionary with the name of a step and the variable
                use_cache. We will use this to determine whether we have to read
                a previous parquet table to concatenate before saving the cached
                datasets.

        Raises:
            ValueError: If the path is not a directory.
        """
        self._path = Path(path)
        if not self._path.exists():
            self._path.mkdir(parents=True, exist_ok=True)
            for step in leaf_steps:
                (self._path / step).mkdir(parents=True, exist_ok=True)

        if not self._path.is_dir():
            raise ValueError(f"The path should be a directory, not a file: {path}")

        self._buffers: Dict[str, List[Dict[str, Any]]] = {
            step: [] for step in leaf_steps
        }  # noqa: C420
        default_batch_size = (
            buffer_batch_size
            if buffer_batch_size is not None
            else envs.FASTDISTILL_WRITE_BUFFER_BATCH_SIZE
        )
        self._buffers_dump_batch_size: Dict[str, int] = dict.fromkeys(
            leaf_steps,
            default_batch_size,
        )
        self._buffer_last_schema = {}
        self._buffers_last_file: Dict[str, int] = dict.fromkeys(leaf_steps, 1)
        self._files_needing_schema_rewrite: Dict[str, Set[Path]] = {
            step: set() for step in leaf_steps
        }
        self._steps_cached = steps_cached or {}
        self._logger = logging.getLogger("fastdistill.write_buffer")

    def _get_filename(self, step_name: str) -> Path:
        """Creates the filename for the step.

        Args:
            step_name: Name of the step to which the data belongs to.

        Returns:
            Filename for the step.
        """
        return self._path / f"{step_name}.parquet"

    def is_full(self, step_name: str) -> bool:
        """Checks the buffers that are full so that those can be written to the file.

        Returns:
            Whether the buffer is full.
        """
        return len(self._buffers[step_name]) >= self._buffers_dump_batch_size[step_name]

    def add_batch(self, batch: "_Batch") -> None:
        """Adds a batch to the buffer and writes the buffer to the file if it's full.

        Args:
            batch: batch to add to the buffer.
        """
        step_name = batch.step_name
        data = batch.data[0]
        self._buffers[step_name].extend(data)
        self._logger.debug(
            f"Added batch to write buffer for step '{step_name}' with {len(data)} rows."
        )
        if self.is_full(step_name):
            self._logger.debug(
                f"Buffer for step '{step_name}' is full (rows: {len(self._buffers[step_name])},"
                f" full: {self._buffers_dump_batch_size[step_name]}), writing to file..."
            )
            self._write(step_name)

    def _write(self, step_name: str) -> None:
        """Writes the content to the file and cleans the buffer.

        Args:
            step_name (str): Name of the step to which the data pertains.
        """
        step_parquet_dir = Path(self._path, step_name)
        if not step_parquet_dir.exists():
            self._logger.debug(
                f"Creating directory for step '{step_name}' parquet files..."
            )
            step_parquet_dir.mkdir()

        buffers = self._buffers[step_name]

        # Proactively detect nested dicts by sampling the first row to avoid
        # exception-driven control flow with pa.Table.from_pylist
        needs_flatten = buffers and any(
            isinstance(v, dict) for v in buffers[0].values()
        )
        if needs_flatten:
            buffers = [flatten_dict(buf) for buf in buffers]

        table = pa.Table.from_pylist(buffers)

        last_schema = self._buffer_last_schema.get(step_name)
        if last_schema is None:
            self._buffer_last_schema[step_name] = table.schema
        else:
            if not last_schema.equals(table.schema):
                if set(last_schema.names) == set(table.schema.names):
                    table = table.select(last_schema.names)
                else:
                    new_schema = pa.unify_schemas([last_schema, table.schema])
                    self._buffer_last_schema[step_name] = new_schema
                    table = table.cast(new_schema)
                    # All previously written files need schema rewrite
                    step_parquet_dir = Path(self._path, step_name)
                    if step_parquet_dir.exists():
                        self._files_needing_schema_rewrite[step_name] = set(
                            list_files_in_dir(step_parquet_dir)
                        )

        next_file_number = self._buffers_last_file[step_name]
        self._buffers_last_file[step_name] = next_file_number + 1

        parquet_file = step_parquet_dir / f"{str(next_file_number).zfill(5)}.parquet"
        if parquet_file.exists():
            # If the file already exists, due to some error in a pipeline that was cached
            prev_table = pq.read_table(parquet_file)
            # If some columns differ, it means some of the step changed, we won't load the previous table
            # NOTE: If any step has use_cache=False, we cannot assume the previous parquet file is
            # valid, so we will overwrite the previous parquet file. Is this the best option?
            use_cache = False not in self._steps_cached.values()

            if prev_table.column_names == table.column_names and use_cache:
                table = pa.concat_tables([prev_table, table])

        pq.write_table(table, parquet_file)
        self._logger.debug(f"Written to file '{parquet_file}'")

        self._clean_buffer(step_name)

    def _clean_buffer(self, step_name: str) -> None:
        """Cleans the buffer by setting it's content to `None`.

        Args:
            step_name: The name of the buffer to clean.
        """
        self._buffers[step_name] = []

    def close(self) -> None:
        """Closes the buffer by writing the remaining content to the file."""
        for step_name in self._buffers:
            if self._buffers[step_name]:
                self._write(step_name)

            # Only rewrite files that were written with an older schema
            files_to_rewrite = self._files_needing_schema_rewrite.get(step_name, set())
            if files_to_rewrite and step_name in self._buffer_last_schema:
                final_schema = self._buffer_last_schema[step_name]
                for file in files_to_rewrite:
                    if file.exists():
                        table = pq.read_table(file, schema=final_schema)
                        pq.write_table(table, file)
