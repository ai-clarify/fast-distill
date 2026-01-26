#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
venv_dir="${FASTDISTILL_VENV_DIR:-$root/.venv}"
python_bin="${FASTDISTILL_VENV_PYTHON:-python3}"
python_version="${FASTDISTILL_VENV_PYTHON_VERSION:-3.11}"
install_tests="${FASTDISTILL_VENV_AUTO_INSTALL:-1}"
extras="${FASTDISTILL_VENV_EXTRAS:-tests}"

if [[ ! -d "$venv_dir" ]]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv "$venv_dir" --python "$python_version"
  else
    "$python_bin" -m venv "$venv_dir"
  fi
fi

# shellcheck disable=SC1091
if [[ -z "${VIRTUAL_ENV:-}" || "${VIRTUAL_ENV}" != "$venv_dir" ]]; then
  source "$venv_dir/bin/activate"
fi

if [[ "$install_tests" == "1" ]]; then
  stamp_file="$venv_dir/.fastdistill_tests_installed"
  current_hash="$(python - <<'PY'
import hashlib
from pathlib import Path

payload = Path('pyproject.toml').read_bytes()
print(hashlib.sha256(payload).hexdigest())
PY
)"
  previous_hash=""
  if [[ -f "$stamp_file" ]]; then
    previous_hash="$(cat "$stamp_file")"
  fi
  if [[ "$current_hash" != "$previous_hash" ]]; then
    if command -v uv >/dev/null 2>&1; then
      uv pip install -e ".[$extras]"
    else
      python -m pip install -e ".[$extras]"
    fi
    echo "$current_hash" > "$stamp_file"
  fi
fi
