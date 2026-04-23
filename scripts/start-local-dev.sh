#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing .env at ${ENV_FILE}. Copy .env.example to .env first." >&2
  exit 1
fi

"${ROOT_DIR}/scripts/check-system-audio-prereqs.sh"

cleanup() {
  if [[ -n "${WEB_PID:-}" ]] && kill -0 "${WEB_PID}" >/dev/null 2>&1; then
    kill "${WEB_PID}" >/dev/null 2>&1 || true
  fi

  if [[ -n "${AGENT_PID:-}" ]] && kill -0 "${AGENT_PID}" >/dev/null 2>&1; then
    kill "${AGENT_PID}" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

cd "${ROOT_DIR}"

if [[ ! -d "${ROOT_DIR}/web/node_modules" ]]; then
  echo "Installing web dependencies..."
  npm install --prefix "${ROOT_DIR}/web"
fi

echo "Starting local agent..."
(
  cd "${ROOT_DIR}/agent"
  set -a
  # shellcheck disable=SC1091
  source "${ENV_FILE}"
  set +a
  python3 main.py
) &
AGENT_PID=$!

echo "Starting web overlay..."
(
  cd "${ROOT_DIR}/web"
  npm run dev -- --host 127.0.0.1 --port 5173
) &
WEB_PID=$!

echo "Agent PID: ${AGENT_PID}"
echo "Web PID: ${WEB_PID}"
echo "Overlay URL: http://127.0.0.1:5173"
echo "Press Ctrl+C to stop both processes."

wait "${AGENT_PID}" "${WEB_PID}"
