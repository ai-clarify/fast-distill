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

import hashlib
import sqlite3
from typing import List, Optional, Sequence

from pydantic import Field, PrivateAttr
from typing_extensions import override

from distilabel.steps.base import Step, StepInput
from distilabel.steps.fastdistill.utils import stable_json_dumps


class SQLiteExecEval(Step):
    """Execute SQL and optionally compare against gold SQL in a SQLite database.

    Produces exec_pass and gold_match signals for automatic evaluation.
    """

    db_path: str = Field(..., description="Path to the SQLite database file.")
    sql_field: str = Field(default="generation")
    gold_sql_field: str = Field(default="gold_sql")
    exec_pass_field: str = Field(default="exec_pass")
    exec_error_field: str = Field(default="exec_error")
    gold_match_field: str = Field(default="gold_match")
    result_signature_field: str = Field(default="result_signature")
    normalize_order: bool = Field(
        default=True,
        description="Sort rows before comparing to make results order-insensitive.",
    )
    max_rows: Optional[int] = Field(
        default=None,
        description="Optional max number of rows to compare.",
    )

    _conn: sqlite3.Connection = PrivateAttr(None)

    @property
    def inputs(self) -> List[str]:
        return [self.sql_field]

    @property
    def outputs(self) -> List[str]:
        return [
            self.exec_pass_field,
            self.exec_error_field,
            self.gold_match_field,
            self.result_signature_field,
        ]

    def load(self) -> None:
        super().load()
        self._conn = sqlite3.connect(self.db_path)

    def unload(self) -> None:
        if self._conn is not None:
            self._conn.close()

    def _normalize_rows(self, rows: Sequence[Sequence[object]]) -> List[List[object]]:
        normalized = [list(row) for row in rows]
        if self.normalize_order:
            normalized = sorted(normalized, key=lambda row: [str(item) for item in row])
        if self.max_rows is not None:
            normalized = normalized[: self.max_rows]
        return normalized

    def _exec_sql(self, sql: str) -> List[List[object]]:
        cursor = self._conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return self._normalize_rows(rows)

    def _signature(self, rows: List[List[object]]) -> str:
        payload = stable_json_dumps(rows)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        for row in inputs:
            sql = row.get(self.sql_field)
            exec_pass = True
            exec_error = None
            result_rows: List[List[object]] = []
            try:
                result_rows = self._exec_sql(sql)
            except Exception as exc:  # noqa: BLE001
                exec_pass = False
                exec_error = str(exc)

            row[self.exec_pass_field] = exec_pass
            row[self.exec_error_field] = exec_error
            row[self.result_signature_field] = (
                self._signature(result_rows) if exec_pass else None
            )

            gold_sql = row.get(self.gold_sql_field)
            if gold_sql:
                if not exec_pass:
                    row[self.gold_match_field] = False
                    continue
                try:
                    gold_rows = self._exec_sql(gold_sql)
                except Exception:  # noqa: BLE001
                    row[self.gold_match_field] = False
                    continue
                row[self.gold_match_field] = result_rows == gold_rows
            else:
                row[self.gold_match_field] = None
        yield inputs
