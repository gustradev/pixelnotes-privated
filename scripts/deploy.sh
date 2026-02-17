#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENVIRONMENT="${1:-staging}"

cd "$ROOT_DIR"

if [[ "$ENVIRONMENT" == "dev" ]]; then
  docker compose -f docker-compose.yml -f infra/docker-compose.dev.yml up -d --build
elif [[ "$ENVIRONMENT" == "prod" ]]; then
  docker compose -f docker-compose.yml -f infra/docker-compose.prod.yml up -d --build
else
  docker compose -f docker-compose.yml -f infra/docker-compose.staging.yml up -d --build
fi

docker compose ps
