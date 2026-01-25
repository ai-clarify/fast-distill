# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

from fastdistill.utils.wikisql import (
    format_schema,
    sql_from_wikisql,
    table_name_from_id,
)


def test_table_name_from_id() -> None:
    assert table_name_from_id("1-1000181-1") == "table_1_1000181_1"


def test_format_schema() -> None:
    schema = format_schema("table_x", ["A", "B"], ["text", "integer"])
    assert schema == "table_x(col0:text [A], col1:integer [B])"


def test_sql_from_wikisql() -> None:
    sql_dict = {"sel": 1, "agg": 0, "conds": [[0, 0, "SOUTH"], [2, 2, "10"]]}
    sql = sql_from_wikisql(sql_dict, "table_x", ["text", "text", "integer"])
    assert sql == "SELECT col1 FROM table_x WHERE col0 = 'south' AND col2 < 10"


def test_sql_from_wikisql_with_agg() -> None:
    sql_dict = {"sel": 0, "agg": 3, "conds": []}
    sql = sql_from_wikisql(sql_dict, "table_x", ["text"])
    assert sql == "SELECT COUNT(col0) FROM table_x"


def test_sql_from_wikisql_unsupported_op() -> None:
    sql_dict = {"sel": 0, "agg": 0, "conds": [[0, 3, "x"]]}
    with pytest.raises(ValueError):
        sql_from_wikisql(sql_dict, "table_x", ["text"])
