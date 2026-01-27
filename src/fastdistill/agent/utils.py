# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

import re
from datetime import datetime, timezone


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return cleaned.strip("-")


def make_run_id(name: str | None = None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if name:
        slug = slugify(name)
        if slug:
            return f"{stamp}-{slug}"
    return stamp
