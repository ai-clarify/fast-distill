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

import re
from dataclasses import dataclass
from typing import Iterable, Tuple

_SQL_FENCE_RE = re.compile(r"```\s*(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_SQL_PREFIX_RE = re.compile(r"(?is)\bsql\s*[:：]\s*")
_SQL_LINE_RE = re.compile(r"(?im)^\s*(select|with|insert|update|delete)\b")
_SQL_INLINE_RE = re.compile(r"(?is)\b(select|with|insert|update|delete)\b")


@dataclass(frozen=True)
class SqlOutputCleaner:
    think_tags: Tuple[str, ...] = ("think", "analysis", "reasoning", "thought")
    stop_markers: Tuple[str, ...] = (
        "explanation:",
        "reasoning:",
        "analysis:",
        "answer:",
        "final:",
        "notes:",
    )
    require_sql_keyword: bool = True

    def clean(self, text: str) -> str:
        return clean_sql_output(
            text,
            think_tags=self.think_tags,
            stop_markers=self.stop_markers,
            require_sql_keyword=self.require_sql_keyword,
        )


def _strip_tag_blocks(text: str, tags: Iterable[str]) -> str:
    cleaned = text
    for tag in tags:
        cleaned = re.sub(
            rf"(?is)<{re.escape(tag)}>.*?</{re.escape(tag)}>",
            "",
            cleaned,
        )
    return cleaned


def _strip_tag_markers(text: str, tags: Iterable[str]) -> str:
    tag_pattern = "|".join(re.escape(tag) for tag in tags)
    if not tag_pattern:
        return text
    return re.sub(rf"(?is)</?(?:{tag_pattern})>", "", text)


def _extract_fenced_sql(text: str) -> str | None:
    match = _SQL_FENCE_RE.search(text)
    if not match:
        return None
    return match.group(1).strip()


def _extract_after_prefix(text: str) -> str | None:
    match = _SQL_PREFIX_RE.search(text)
    if not match:
        return None
    return text[match.end() :].strip()


def _extract_from_line_start(text: str) -> str | None:
    match = _SQL_LINE_RE.search(text)
    if not match:
        return None
    return text[match.start() :].strip()


def _extract_from_inline_keyword(text: str) -> str | None:
    match = _SQL_INLINE_RE.search(text)
    if not match:
        return None
    return text[match.start() :].strip()


def _trim_trailing(sql: str, stop_markers: Iterable[str]) -> str:
    cleaned = sql.strip()
    if not cleaned:
        return cleaned
    if "```" in cleaned:
        cleaned = cleaned.split("```", 1)[0].strip()
    lower = cleaned.lower()
    for marker in stop_markers:
        idx = lower.find(marker)
        if idx > 0:
            cleaned = cleaned[:idx].strip()
            lower = cleaned.lower()
    if ";" in cleaned:
        head, tail = cleaned.split(";", 1)
        if tail.strip():
            cleaned = f"{head.strip()};"
    return cleaned.strip()


def clean_sql_output(
    text: str,
    *,
    think_tags: Iterable[str] = ("think", "analysis", "reasoning", "thought"),
    stop_markers: Iterable[str] = (
        "explanation:",
        "reasoning:",
        "analysis:",
        "answer:",
        "final:",
        "notes:",
    ),
    require_sql_keyword: bool = True,
) -> str:
    if not text:
        return ""

    cleaned = text.strip()
    if not cleaned:
        return ""

    cleaned = _strip_tag_blocks(cleaned, think_tags)
    cleaned = _strip_tag_markers(cleaned, think_tags).strip()

    candidate = _extract_fenced_sql(cleaned)
    if candidate is None:
        candidate = _extract_after_prefix(cleaned)
    if candidate is None:
        candidate = _extract_from_line_start(cleaned)
    if candidate is None:
        candidate = _extract_from_inline_keyword(cleaned)
    if candidate is None:
        candidate = cleaned

    candidate = _SQL_PREFIX_RE.sub("", candidate).strip()
    candidate = _trim_trailing(candidate, stop_markers)

    if require_sql_keyword and not _SQL_INLINE_RE.search(candidate or ""):
        return ""
    return candidate.strip()
