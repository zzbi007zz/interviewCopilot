# Interview Copilot

> **Status:** Phase 07 complete — all MVP features delivered, tested, and packaged for local use.

Hybrid local-agent + web-overlay interview assistant that captures audio, detects language/intent, generates answer suggestions in real-time, and streams results to a browser overlay — all while keeping API keys local.

## Features

- **Local Audio Capture** — capture system audio via configurable device (BlackHole, etc.)
- **ASR Pipeline** — primary provider (Deepgram) with automatic local fallback
- **Language Detection** — auto-detect interview language
- **Intent Classification** — identify technical vs behavioral question types
- **Answer Generation** — dual-option answers (A/B) with quality checks
- **Web Overlay UI** — real-time React/TypeScript client via WebSocket
- **Health Diagnostics** — runtime status snapshots with explicit error taxonomy
- **Zero Storage** — no transcripts/answers persisted by default
- **Localhost-Only** — no remote exposure; keys stay local

## Project Status

| Plan | Status | Progress | QA Reports |
|---|---|---|---|
| [Hybrid Interview Copilot Implementation](plans/260423-1735-hybrid-interview-copilot-implementation/plan.md) | ✅ Completed | 7/7 phases (100%) | [reports/](plans/reports/) |
| [Project Harness Agent Team](plans/260423-1009-project-harness-agent-team/plan.md) | 📋 Pending | 0/4 phases (0%) | Future work |

All phases from Phase 01 (bootstrap) through Phase 07 (integration/hardening) have passed QA gates and tracking updates.

## Quick Start

### Prerequisites

- **Python 3.9+** with `pip`
- **Node.js 18+** with `npm`
- **Audio device** (e.g., BlackHole for macOS system audio routing)
- **API keys** for ASR (Deepgram) and answer generation (Anthropic)

### Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:zzbi007zz/interviewCopilot.git
   cd interviewCopilot
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Install Python dependencies:**
   ```bash
   cd agent
   pip install -r requirements.txt
   cd ..
   ```

4. **Install web dependencies:**
   ```bash
   cd web
   npm install
   cd ..
   ```

5. **Run preflight checks:**
   ```bash
   ./scripts/check-system-audio-prereqs.sh
   ```

### Run Locally

```bash
./scripts/start-local-dev.sh
```

This starts:
- **Local agent** on `127.0.0.1:8765` (WebSocket)
- **Web overlay** on `http://127.0.0.1:5173`

Open the overlay URL in your browser and start an interview session. The overlay will display:
- Connection status
- Agent runtime status
- Latest detected question
- Option A / Option B answer suggestions
- Partial transcript preview

Press `Ctrl+C` to stop both processes.

## Configuration

Edit `.env` to customize runtime behavior:

| Variable | Default | Description |
|---|---|---|
| `DEEPGRAM_KEY` | (required) | Deepgram API key for ASR |
| `ANTHROPIC_KEY` | (required) | Anthropic API key for answer generation |
| `LOCAL_AGENT_WS_HOST` | `127.0.0.1` | WebSocket host (must stay local) |
| `LOCAL_AGENT_WS_PORT` | `8765` | WebSocket port |
| `AUDIO_DEVICE_NAME` | `BlackHole` | System audio capture device |
| `AUDIO_SAMPLE_RATE` | `16000` | Audio sample rate (Hz) |
| `ASR_PRIMARY_TIMEOUT_MS` | `3000` | Primary ASR timeout before fallback |
| `ASR_FALLBACK_ENABLED` | `true` | Enable local fallback ASR |
| `ZERO_STORAGE_MODE` | `true` | Disable transcript/answer persistence |

See [.env.example](.env.example) for full list.

## Architecture

```
┌─────────────────┐
│  System Audio   │
│   (BlackHole)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Local Agent    │
│  (Python)       │
│                 │
│  • Audio        │
│  • ASR          │
│  • Language     │
│  • Intent       │
│  • Answers      │
│  • WebSocket    │
└────────┬────────┘
         │ ws://127.0.0.1:8765
         v
┌─────────────────┐
│  Web Overlay    │
│  (React/TS)     │
│                 │
│  • Status       │
│  • Question     │
│  • Option A/B   │
│  • Reconnect    │
└─────────────────┘
```

See [docs/system-architecture.md](docs/system-architecture.md) for detailed component breakdown.

## Testing

**Python tests:**
```bash
python3 -m unittest tests/test_phase_05_answer_modules.py tests/test_phase_07_agent_websocket_flow.py
```

**Web tests:**
```bash
cd web
npm test
```

**Web build verification:**
```bash
cd web
npm run build
```

All test suites passed at Phase 07 completion.

## Documentation

- [Project Overview (PDR)](docs/project-overview-pdr.md) — product requirements and design decisions
- [System Architecture](docs/system-architecture.md) — component interactions and data flow
- [Development Roadmap](docs/development-roadmap.md) — phase completion history
- [Project Changelog](docs/project-changelog.md) — feature/fix/update log
- [Deployment Guide](docs/deployment-guide.md) — setup, troubleshooting, latency benchmarks
- [Code Standards](docs/code-standards.md) — implementation conventions

## Development Plans

All phase plans and QA reports are preserved in `plans/`:

- [Implementation Plan](plans/260423-1735-hybrid-interview-copilot-implementation/plan.md)
- [Phase Reports](plans/reports/)

## Performance

Local baseline latency measured at Phase 07:
- **Median:** `0.020 ms` (transcript → answer routing)
- **Test method:** 25-sample local execution of implemented pipeline
- **Note:** Full microphone/network/provider round-trip depends on live environment

See [QA Gate Report](plans/reports/qa-gate-2026-04-23-phase-07-integrate-end-to-end-harden-validate-and-package.md) for measurement methodology.

## Security

- API keys stored in `.env` (never committed)
- Localhost-only WebSocket (no remote exposure by default)
- Zero-storage mode enabled by default
- Client receives sanitized error messages only
- No stack traces or raw payloads exposed to UI

## License

MIT

## Contributing

This project follows a phased delivery harness with mandatory QA gates. See [CLAUDE.md](CLAUDE.md) for team orchestration rules.

## Acknowledgments

Built with Claude Code using a harness-controlled phased implementation approach.
