#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "[FAIL] Missing .env file at ${ENV_FILE}" >&2
  echo "Copy .env.example to .env before running preflight." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "${ENV_FILE}"

require_var() {
  local name="$1"
  local value="${!name:-}"
  if [[ -z "${value}" ]]; then
    echo "[FAIL] Required env var is empty: ${name}" >&2
    exit 1
  fi
}

require_num_var() {
  local name="$1"
  local value="${!name:-}"
  if ! [[ "${value}" =~ ^[0-9]+$ ]]; then
    echo "[FAIL] ${name} must be a positive integer (got: ${value:-<empty>})" >&2
    exit 1
  fi
  if [[ "${value}" -le 0 ]]; then
    echo "[FAIL] ${name} must be > 0" >&2
    exit 1
  fi
}

require_var "LOCAL_AGENT_WS_HOST"
require_var "LOCAL_AGENT_WS_PORT"
require_var "AUDIO_DEVICE_NAME"
require_num_var "AUDIO_SAMPLE_RATE"
require_num_var "AUDIO_CHUNK_MS"

if [[ "${LOCAL_AGENT_WS_HOST}" != "127.0.0.1" && "${LOCAL_AGENT_WS_HOST}" != "localhost" ]]; then
  echo "[FAIL] LOCAL_AGENT_WS_HOST must remain local (127.0.0.1 or localhost)." >&2
  exit 1
fi

if ! [[ "${LOCAL_AGENT_WS_PORT}" =~ ^[0-9]+$ ]]; then
  echo "[FAIL] LOCAL_AGENT_WS_PORT must be numeric." >&2
  exit 1
fi

if [[ "${LOCAL_AGENT_WS_PORT}" -lt 1 || "${LOCAL_AGENT_WS_PORT}" -gt 65535 ]]; then
  echo "[FAIL] LOCAL_AGENT_WS_PORT must be between 1 and 65535." >&2
  exit 1
fi

if [[ "${AUDIO_DEVICE_NAME}" == "BlackHole" ]]; then
  echo "[WARN] AUDIO_DEVICE_NAME is still 'BlackHole'. Confirm this device exists on your machine."
fi

if command -v ffmpeg >/dev/null 2>&1; then
  echo "[OK] ffmpeg found: $(command -v ffmpeg)"
else
  echo "[WARN] ffmpeg not found (optional for current runtime, useful for diagnostics)."
fi

if command -v python3 >/dev/null 2>&1; then
  echo "[OK] python3 found: $(python3 --version 2>&1)"
else
  echo "[FAIL] python3 is required." >&2
  exit 1
fi

if command -v node >/dev/null 2>&1; then
  echo "[OK] node found: $(node --version 2>&1)"
else
  echo "[FAIL] node is required for web overlay." >&2
  exit 1
fi

if command -v npm >/dev/null 2>&1; then
  echo "[OK] npm found: $(npm --version 2>&1)"
else
  echo "[FAIL] npm is required for web overlay." >&2
  exit 1
fi

echo "[PASS] Audio/runtime preflight checks passed."
