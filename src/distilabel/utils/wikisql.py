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

from typing import Iterable, List, Mapping, Optional, Sequence

AGG_OPS: Sequence[str] = ("", "MAX", "MIN", "COUNT", "SUM", "AVG")
COND_OPS: Sequence[str] = ("=", ">", "<", "OP")
NUMERIC_TYPES = {"real", "integer", "number", "float"}


def table_name_from_id(table_id: str) -> str:
    return f"table_{table_id.replace('-', '_')}"


def format_schema(table_name: str, headers: Sequence[str], types: Sequence[str]) -> str:
    columns = []
    for idx, header in enumerate(headers):
        col_type = types[idx] if idx < len(types) else "text"
        columns.append(f"col{idx}:{col_type} [{header}]")
    return f"{table_name}(" + ", ".join(columns) + ")"


def _literal_sql(value: object, col_type: Optional[str]) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    value_str = str(value)
    if col_type and col_type.lower() in NUMERIC_TYPES:
        try:
            numeric = float(value_str)
        except ValueError:
            numeric = None
        if numeric is not None:
            if numeric.is_integer():
                return str(int(numeric))
            return str(numeric)
    value_str = value_str.lower().replace("'", "''")
    return f"'{value_str}'"


def sql_from_wikisql(
    sql_dict: Mapping[str, object],
    table_name: str,
    types: Optional[Sequence[str]] = None,
    supported_ops: Iterable[int] = (0, 1, 2),
) -> str:
    if "sel" not in sql_dict or "agg" not in sql_dict or "conds" not in sql_dict:
        raise ValueError("sql_dict missing required keys")

    sel_idx = int(sql_dict["sel"])
    agg_idx = int(sql_dict["agg"])
    if agg_idx < 0 or agg_idx >= len(AGG_OPS):
        raise ValueError(f"unsupported agg index: {agg_idx}")

    select_expr = f"col{sel_idx}"
    agg = AGG_OPS[agg_idx]
    if agg:
        select_expr = f"{agg}({select_expr})"

    conds = []
    for cond in sql_dict["conds"]:
        col_idx, op_idx, value = cond
        col_idx = int(col_idx)
        op_idx = int(op_idx)
        if op_idx not in supported_ops or op_idx >= len(COND_OPS):
            raise ValueError(f"unsupported op index: {op_idx}")
        op = COND_OPS[op_idx]
        col_type = types[col_idx] if types and col_idx < len(types) else None
        value_sql = _literal_sql(value, col_type)
        conds.append(f"col{col_idx} {op} {value_sql}")

    query = f"SELECT {select_expr} FROM {table_name}"
    if conds:
        query += " WHERE " + " AND ".join(conds)
    return query
