#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR/backend"
"$ROOT_DIR/.venv/bin/python" -m pip install -q -r requirements.txt -r requirements-dev.txt
PYTHONPATH=. "$ROOT_DIR/.venv/bin/python" -m pytest ../tests/backend -q

cd "$ROOT_DIR/frontend"
flutter pub get
flutter analyze
