# Copyright 2023-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import tarfile
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, List

from distilabel.utils.serialization import write_yaml
from distilabel.utils.wikisql import format_schema, sql_from_wikisql, table_name_from_id

WIKISQL_URL = "https://raw.githubusercontent.com/salesforce/WikiSQL/master/data.tar.bz2"


def _download_if_missing(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return
    print("downloading_wikisql_archive=", WIKISQL_URL)
    urllib.request.urlretrieve(WIKISQL_URL, target)


def _extract_members(archive: Path, dest: Path, members: Iterable[str]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:bz2") as tar:
        for name in members:
            target = dest / name
            if target.exists():
                continue
            tar.extract(name, path=dest)


def _load_tables(path: Path) -> Dict[str, dict]:
    tables: Dict[str, dict] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            tables[row["id"]] = row
    return tables


def _load_samples(path: Path, tables: Dict[str, dict]) -> List[dict]:
    samples: List[dict] = []
    skipped = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            table_id = row["table_id"]
            table = tables.get(table_id)
            if table is None:
                skipped += 1
                continue
            try:
                table_name = table_name_from_id(table_id)
                sql = sql_from_wikisql(row["sql"], table_name, table.get("types"))
            except Exception:
                skipped += 1
                continue
            schema = format_schema(
                table_name,
                table.get("header", []),
                table.get("types", []),
            )
            samples.append(
                {
                    "table_id": table_id,
                    "schema": schema,
                    "instruction": row["question"],
                    "gold_sql": sql,
                }
            )
    if skipped:
        print(f"skipped_samples={skipped}")
    return samples


def _sample_rows(rows: List[dict], count: int, seed: int) -> List[dict]:
    rng = random.Random(seed)
    if count >= len(rows):
        rng.shuffle(rows)
        return rows
    selected = rng.sample(rows, count)
    return selected


def _write_jsonl(path: Path, rows: List[dict], prefix: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for idx, row in enumerate(rows):
            payload = dict(row)
            payload["task_id"] = f"{prefix}-{idx:06d}"
            payload["system_prompt"] = "Return SQL only."
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare WikiSQL 1k datasets")
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    root = Path(
        os.getenv(
            "FASTDISTILL_WIKISQL_ROOT",
            Path.home() / ".cache" / "fastdistill" / "datasets" / "wikisql",
        )
    )
    archive = root / "data.tar.bz2"
    _download_if_missing(archive)

    raw_dir = root / "raw"
    members = [
        "data/train.jsonl",
        "data/dev.jsonl",
        "data/train.tables.jsonl",
        "data/dev.tables.jsonl",
        "data/train.db",
        "data/dev.db",
    ]
    _extract_members(archive, raw_dir, members)

    output_dir = args.output_dir or root / "wikisql_1k"
    output_dir.mkdir(parents=True, exist_ok=True)

    train_tables = _load_tables(raw_dir / "data" / "train.tables.jsonl")
    dev_tables = _load_tables(raw_dir / "data" / "dev.tables.jsonl")

    train_rows = _load_samples(raw_dir / "data" / "train.jsonl", train_tables)
    dev_rows = _load_samples(raw_dir / "data" / "dev.jsonl", dev_tables)

    train_selected = _sample_rows(train_rows, args.samples, args.seed)
    dev_selected = _sample_rows(dev_rows, args.samples, args.seed + 1)

    _write_jsonl(output_dir / "train.jsonl", train_selected, "wikisql-train")
    _write_jsonl(output_dir / "eval.jsonl", dev_selected, "wikisql-eval")

    shutil.copy2(raw_dir / "data" / "train.db", output_dir / "train.db")
    shutil.copy2(raw_dir / "data" / "dev.db", output_dir / "eval.db")

    meta = {
        "source": WIKISQL_URL,
        "train_samples": len(train_selected),
        "eval_samples": len(dev_selected),
        "seed": args.seed,
        "output_dir": str(output_dir),
    }
    write_yaml(output_dir / "dataset.yaml", meta)

    print("output_dir=", output_dir)
    print("train_path=", output_dir / "train.jsonl")
    print("eval_path=", output_dir / "eval.jsonl")
    print("train_db=", output_dir / "train.db")
    print("eval_db=", output_dir / "eval.db")


if __name__ == "__main__":
    main()
