# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import json
from typing import Any


def stable_json_dumps(value: Any) -> str:
    """Serialize values deterministically for hashing/canonicalization.

    Falls back to string conversion for non-JSON-serializable values.
    """
    try:
        return json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
        )
    except TypeError:
        return json.dumps(
            str(value),
            ensure_ascii=True,
            separators=(",", ":"),
        )
