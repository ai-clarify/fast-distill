#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$script_dir/ensure_venv.sh"

changes="$(
  {
    git diff --name-only --diff-filter=AMRT
    git diff --name-only --cached --diff-filter=AMRT
  } | sort -u
)"

if [[ -z "$changes" ]]; then
  echo "No changes detected."
  exit 0
fi

declare -A seen=()
declare -a tests=()

add_test() {
  local path="$1"
  if [[ -n "$path" && -f "$path" && -z "${seen[$path]:-}" ]]; then
    tests+=("$path")
    seen["$path"]=1
  fi
}

while IFS= read -r path; do
  if [[ -z "$path" ]]; then
    continue
  fi
  if [[ "$path" == tests/* && "$path" == *.py ]]; then
    add_test "$path"
    continue
  fi
  if [[ "$path" == src/fastdistill/* && "$path" == *.py ]]; then
    module="${path#src/fastdistill/}"
    module="${module%.py}"
    module="${module//\//.}"
    while IFS= read -r match; do
      add_test "$match"
    done < <(rg -l "fastdistill\\.${module}" tests || true)
  fi
done <<< "$changes"

if [[ ${#tests[@]} -eq 0 ]]; then
  echo "No related tests found for current changes."
  echo "Consider running: pytest"
  exit 0
fi

echo "Running tests: ${tests[*]}"
pytest "${tests[@]}"
