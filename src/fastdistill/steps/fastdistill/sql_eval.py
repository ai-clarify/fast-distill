# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import hashlib
import sqlite3
from collections import OrderedDict
from typing import List, Optional, Sequence

from pydantic import Field, PrivateAttr
from typing_extensions import override

from fastdistill.steps.base import Step, StepInput
from fastdistill.steps.fastdistill.utils import stable_json_dumps


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
    cache_gold_results: bool = Field(
        default=True,
        description="Cache gold SQL results to avoid repeated execution.",
    )
    max_cached_gold: int = Field(
        default=1024,
        ge=1,
        description="Maximum number of cached gold SQL results.",
    )

    _conn: sqlite3.Connection = PrivateAttr(None)
    _gold_cache: OrderedDict[str, List[List[object]]] = PrivateAttr(
        default_factory=OrderedDict
    )

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
        if self.cache_gold_results:
            self._gold_cache.clear()

    def unload(self) -> None:
        if self._conn is not None:
            self._conn.close()
        if self.cache_gold_results:
            self._gold_cache.clear()

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

    def _try_exec(
        self, sql: Optional[str]
    ) -> tuple[bool, Optional[str], List[List[object]]]:
        try:
            result_rows = self._exec_sql(sql)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001
            return False, str(exc), []
        return True, None, result_rows

    def _get_gold_rows(self, gold_sql: str) -> List[List[object]]:
        if self.cache_gold_results:
            cached = self._gold_cache.get(gold_sql)
            if cached is not None:
                self._gold_cache.move_to_end(gold_sql)
                return cached

        gold_rows = self._exec_sql(gold_sql)
        if self.cache_gold_results:
            self._gold_cache[gold_sql] = gold_rows
            if len(self._gold_cache) > self.max_cached_gold:
                self._gold_cache.popitem(last=False)
        return gold_rows

    def _evaluate_gold_match(
        self,
        *,
        gold_sql: Optional[str],
        exec_pass: bool,
        result_rows: List[List[object]],
    ) -> Optional[bool]:
        if not gold_sql:
            return None
        if not exec_pass:
            return False
        try:
            gold_rows = self._get_gold_rows(gold_sql)
        except Exception:  # noqa: BLE001
            return False
        return result_rows == gold_rows

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        for row in inputs:
            sql = row.get(self.sql_field)
            exec_pass, exec_error, result_rows = self._try_exec(sql)

            row[self.exec_pass_field] = exec_pass
            row[self.exec_error_field] = exec_error
            row[self.result_signature_field] = (
                self._signature(result_rows) if exec_pass else None
            )

            row[self.gold_match_field] = self._evaluate_gold_match(
                gold_sql=row.get(self.gold_sql_field),
                exec_pass=exec_pass,
                result_rows=result_rows,
            )
        yield inputs
