# Cross-Platform Interview Copilot — Architecture Design (BRIEF-6)

---

## 1. Tóm tắt kiến trúc chung

Pipeline: **Audio Capture → Streaming ASR → Lang Detect → Intent Extract → Answer Gen → UI Overlay**

- macOS dùng system loopback (BlackHole); Web dùng tab audio capture
- ASR cloud (Deepgram/Whisper API) cho tốc độ; local fallback khi offline
- LLM gen answer: Claude/GPT với QC-domain prompt
- UI: floating overlay ≤300px, zero-storage mode

---

## 2. Sơ đồ Pipeline (ASCII)

```
[Meeting Audio]
      │
      ▼
[Audio Capture Layer]
  macOS: CoreAudio + BlackHole
  Web:   getDisplayMedia(audio) / getUserMedia
      │
      ▼ (PCM chunks, 250ms)
[Streaming ASR]
  Cloud: Deepgram Nova-2 / Whisper API
  Local: whisper.cpp (fallback)
      │
      ▼ (partial transcript)
[Lang Detect + Translate]
  langdetect → EN↔VI (Google Translate API / LibreTranslate)
      │
      ▼
[Intent Classifier]
  Regex + LLM classify: question_type, keywords
      │
      ▼
[Answer Generator]
  LLM (Claude Sonnet) + QC prompt template
      │
      ▼
[UI Render]
  macOS: NSPanel overlay
  Web:   Floating div / Chrome Extension popup
```

---

## 3. Ba kiến trúc — Bảng so sánh

| Tiêu chí | macOS Native | Web-only | Hybrid (Top-1) |
|---|---|---|---|
| Audio capture | ✅ CoreAudio + BlackHole (full system) | ⚠️ Tab audio only, no system audio | ✅ Local agent → system audio |
| Latency | ✅ ~1s | ⚠️ ~1.5–2s | ✅ ~1.2s |
| Cross-device | ❌ macOS only | ✅ Any browser | ✅ Agent local + Web UI |
| Setup friction | ❌ Install BlackHole + app | ✅ Zero install | ⚠️ Install agent (one-time) |
| Privacy | ✅ Local-first option | ⚠️ Audio via browser | ✅ Audio stays local |
| Offline | ✅ whisper.cpp | ❌ | ✅ Partial |
| Maintainability | ❌ Swift + Obj-C | ✅ JS/TS | ✅ Python agent + React UI |

---

## 4. Top-1: **Hybrid Architecture**

**Lý do:** Kết hợp ưu điểm của cả hai — system audio capture chất lượng cao từ local agent (Python), giao diện web linh hoạt chạy mọi trình duyệt. Phù hợp cho môi trường freelance/interview nhiều nơi, nhiều thiết bị.

---

## 5. Tech Stack

| Layer | macOS component | Web component |
|---|---|---|
| Audio capture | BlackHole 2ch + PyAudio | `getDisplayMedia({audio:true})` |
| ASR | Deepgram SDK (Python) | Deepgram JS SDK |
| Translation | `deep-translator` (Python) | DeepL API |
| Intent + Answer | `anthropic` Python SDK | Anthropic JS SDK |
| UI | NSPanel (Swift) / Electron | React + Tailwind floating panel |
| Agent transport | FastAPI WebSocket | WebSocket client |

---

## 6. Pseudo-code

```python
# local_agent.py (Python)
import pyaudio, asyncio, websockets
from deepgram import DeepgramClient
from anthropic import Anthropic

async def run():
    dg = DeepgramClient(DG_KEY)
    claude = Anthropic()
    ws_server = await websockets.serve(handle_ui, "localhost", 8765)

    stream = pyaudio.PyAudio().open(
        input_device_index=BLACKHOLE_IDX,  # system loopback
        format=pyaudio.paInt16, channels=1,
        rate=16000, input=True, frames_per_buffer=4000
    )
    async with dg.transcription.live({"language":"multi"}) as dg_conn:
        while True:
            chunk = stream.read(4000)
            await dg_conn.send(chunk)
            transcript = await dg_conn.receive()
            if transcript.get("is_final"):
                answer = generate_answer(claude, transcript["text"])
                await broadcast(ws_server, answer)

def generate_answer(claude, question):
    return claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role":"user","content": QC_PROMPT.format(q=question)}]
    ).content[0].text
```

---

## 7. QC Prompt Template

```
You are a QC/Automation interview assistant. 
Question: "{q}"
Domain: QA Manual/Automation (Selenium, Playwright, API, CI/CD, bug lifecycle)
Language: match input language (EN or VI)
Reply with 2 options, each 1–3 bullets, max 20 words/bullet.
Format:
Option A: [approach]
- bullet
Option B: [approach]  
- bullet
```

---

## 8. UI Wireframe

```
macOS Overlay (320×200, always-on-top):
┌─────────────────────────────────┐
│ 🎙 Listening...          [⚙][×] │
├─────────────────────────────────┤
│ Q: "Explain POM pattern"        │
│ ──────────────────────────────  │
│ ✅ A: BasePage + PageObjects     │
│   • Separate locators/actions   │
│   • Reusable across test suites │
│ 💡 B: Factory Pattern variant   │
│   • Dynamic page instantiation  │
└─────────────────────────────────┘

Web Panel (Chrome Extension popup / floating div):
[Same layout, injected via content script, z-index:9999]
```

---

## 9. Chiến lược giảm độ trễ

| Kỹ thuật | Giảm ms |
|---|---|
| Deepgram `interim_results=true` | −500ms |
| Stream ASR → LLM song song | −300ms |
| Prompt cache (Claude) cho QC context | −200ms |
| Chunk size 250ms thay 1s | −400ms |
| Pre-warm LLM connection | −100ms |

**Target: ≤1.5s end-to-end**

---

## 10. Rủi ro

| Rủi ro | Mức | Giải pháp |
|---|---|---|
| Web không capture system audio | 🔴 | Dùng tab share + audio, hoặc local agent |
| BlackHole not installed | 🟡 | Script auto-install + hướng dẫn one-time |
| Mic noise làm sai ASR | 🟡 | Noise suppression (RNNoise) trước khi gửi |
| API key lộ (client-side) | 🔴 | Key chỉ ở local agent, không expose web |
| Deepgram latency spike | 🟡 | Fallback sang whisper.cpp local |

---

## 11. Checklist Triển khai

- [ ] Install BlackHole 2ch, set as output device
- [ ] `pip install pyaudio deepgram-sdk anthropic fastapi websockets`
- [ ] Set env: `DEEPGRAM_KEY`, `ANTHROPIC_KEY`
- [ ] Test `local_agent.py` — verify transcript output
- [ ] Build React UI, connect `ws://localhost:8765`
- [ ] Load Chrome extension (manifest v3, content script)
- [ ] Test latency: target ≤1.5s trên Google Meet call
- [ ] Enable `interim_results=true` trong Deepgram config
- [ ] Add noise filter nếu mic quality kém
- [ ] Production: wrap agent as LaunchAgent (macOS autostart)
