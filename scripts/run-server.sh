#!/bin/bash

set -e

echo "🚀 Starting 508 Integrations Server..."

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the server (Pydantic will validate required environment variables)
echo "🌐 Starting FastAPI server on ${HOST:-0.0.0.0}:${PORT:-5080}"
uvicorn src.main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-5080}" \
    --log-level "${LOG_LEVEL:-info}" \
    "${@}"
