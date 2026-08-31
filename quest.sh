#!/usr/bin/env bash
set -euo pipefail

quest_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ -x "$quest_dir/.venv/bin/python" ]]; then
    python="$quest_dir/.venv/bin/python"
elif [[ -x "$quest_dir/.venv/Scripts/python.exe" ]]; then
    python="$quest_dir/.venv/Scripts/python.exe"
else
    printf 'Virtual environment not found. Create it with: python -m venv .venv\n' >&2
    exit 1
fi

exec "$python" "$quest_dir/main.py" "$@"
