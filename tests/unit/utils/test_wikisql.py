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

import pytest

from distilabel.utils.wikisql import format_schema, sql_from_wikisql, table_name_from_id


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
