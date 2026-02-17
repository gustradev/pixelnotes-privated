#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_TAG="${1:?Usage: rollback.sh <image-tag>}"

cd "$ROOT_DIR"

docker compose down

export PIXELNOTES_IMAGE_TAG="$TARGET_TAG"
docker compose up -d

docker compose ps
