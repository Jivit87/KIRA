# KIRA — WhatsApp Mac Agent

> Control your Mac entirely through WhatsApp. Message yourself → intent classified → tools executed → reply streamed back.

Everything runs **100% locally**. No cloud, no data leaves your machine.

---

## Demo

```
You:  /clean my downloads folder and organize files by type

KIRA: 🧠 Analyzing your goal...
      📋 4-step plan ready. Starting...
      ⏳ Step 1: List all files in Downloads
      ⏳ Step 2: Create folders by file type
      ⏳ Step 3: Move files to matching folders
      ⏳ Step 4: Summary
      ✅ Plan complete.
```

```
You:  /delete ~/Downloads/old-project

KIRA: ⚠️ Risky action detected:
      Tool: filesystem_op
      Reason: Filesystem delete operation
      Reply YES to run it or NO to cancel.

You:  yes
KIRA: ✅ Moved ~/Downloads/old-project to Trash
```

---

## How It Works

```
WhatsApp (Saved Messages)
        │  /command
        ▼
  Baileys (Node.js :8766)
        │  POST /message  { text, msg_id, sender }
        ▼
  FastAPI Agent (Python :8765)
    ├── Rate limiter (60 req/min)
    ├── Memory lookup  ──► Mem0 + ChromaDB (local vectors)
    ├── Intent classifier
    │       ├── chat   ──► Groq LLM reply
    │       ├── action ──► LLM picks tool → risk check → run
    │       └── plan   ──► Planner → Executor loop (streams status)
    │
    └── Tool Intelligence Layer (retry + fallback)
            ├── spotify_control   AppleScript
            ├── terminal_run      subprocess
            ├── filesystem_op     pathlib / send2trash
            ├── browser_open      macOS open
            ├── system_control    AppleScript (volume/sleep/lock/wifi)
            ├── vscode_open       code CLI
            ├── app_control       AppleScript (open/quit/focus)
            ├── clipboard_read/write   pbpaste / pbcopy
            ├── calendar_query    AppleScript
            ├── reminder_create   AppleScript
            ├── send_notification AppleScript
            └── screen_capture    screencapture CLI

  Redis  ──── sessions · confirmations · rate-limit counters
  ChromaDB ── long-term semantic memory (embedded, no server)
```

### Language Split

| Component | Language | Why |
|-----------|----------|-----|
| WhatsApp bridge | Node.js | Only JS library with a working WA Web implementation |
| Agent + tools + memory | Python | Best AI/ML ecosystem |
| Vector store | ChromaDB (embedded) | Fully local, no separate server |
| Session state | Redis | Fast key/value with TTL |

---

## Project Structure

```
KIRA/
├── agent/
│   ├── main.py                 # FastAPI app — /message and /health endpoints
│   ├── orchestrator.py         # Message router: chat / action / plan
│   ├── streaming.py            # Streams status messages back to WhatsApp
│   ├── confirmation.py         # Stores and prompts YES/NO for risky actions
│   ├── intent/
│   │   └── classifier.py       # Groq LLM → chat | action | plan
│   ├── planner/
│   │   ├── planner.py          # LLM generates a JSON step-by-step plan
│   │   ├── executor.py         # Runs each step, streams status, returns summary
│   │   └── state.py            # Pauses/resumes plans across messages (Redis)
│   ├── memory/
│   │   ├── mem0_client.py      # Lazy-initialized Mem0 (add + search)
│   │   └── redis_client.py     # Shared Redis connection, rate-limit helpers
│   ├── tools/
│   │   ├── router.py           # tool_name → function dispatch
│   │   ├── spotify.py          # play / pause / next / previous / search / volume
│   │   ├── terminal.py         # shell command with timeout + output cap
│   │   ├── filesystem.py       # list / find / read / move / copy / delete
│   │   ├── browser.py          # open URL or Google search via macOS open
│   │   ├── system.py           # volume (0-100 or mute/low/medium/high) / sleep / lock / wifi / date
│   │   ├── vscode.py           # open file or folder in VS Code
│   │   ├── app_control.py      # open / quit / focus any app
│   │   ├── clipboard.py        # pbpaste / pbcopy
│   │   ├── calendar.py         # query today's events, create reminders
│   │   ├── notifications.py    # macOS banner notification
│   │   └── screen.py           # screencapture → base64
│   ├── tool_intelligence/
│   │   └── router.py           # 2-retry + fallback routing per tool
│   ├── middleware/
│   │   └── rate_limiter.py     # 60 req/min sliding-window middleware
│   └── utils/
│       ├── risk_detector.py    # Layer 1: regex hardcodes, Layer 2: Groq LLM scoring
│       ├── formatter.py        # Strip markdown, truncate to 3000 chars for WhatsApp
│       └── logger.py           # Timestamped stdout logger
├── baileys/
│   ├── client.js               # WA WebSocket, QR auth, safe reconnect (3s backoff)
│   ├── listener.js             # Watches Saved Messages, POSTs { text, msg_id, sender }
│   └── sender.js               # Express :8766, receives text from agent → sendMessage
├── launchagents/               # macOS LaunchAgent plists (auto-start at login)
├── Makefile                    # start / stop / logs / install / uninstall
├── docker-compose.yml          # Optional: ChromaDB as a Docker container
├── config.yaml                 # Central config reference
└── .env                        # API keys and service URLs
```

---

## Prerequisites

| Requirement | Install |
|-------------|---------|
| macOS | Required (tools use AppleScript + macOS CLI) |
| Node.js 18+ | `brew install node` |
| Python 3.11+ | `brew install python@3.11` |
| Redis | `brew install redis` |
| Ollama | `brew install ollama` |
| Groq API key | [console.groq.com](https://console.groq.com) |

---

## Setup

### 1. Clone

```bash
git clone https://github.com/Jivit87/KIRA.git
cd KIRA
```

### 2. Environment variables

Create/edit `.env` in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
OLLAMA_URL=http://localhost:11434
REDIS_URL=redis://localhost:6379
CHROMA_PATH=./agent/chroma_db
```

### 3. Install dependencies

```bash
# Python virtualenv + packages
cd agent && python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..

# Node packages
cd baileys && npm install && cd ..
```

### 4. Start background services

```bash
# Redis
brew services start redis

# Ollama + embedding model
ollama serve &
ollama pull nomic-embed-text
```

---

## Running

```bash
make start    # Starts Python agent + Baileys (ChromaDB runs embedded)
make logs     # Tail both log files live
make stop     # Kill all services
```

> **First run only:** A QR code appears in the Baileys log. Scan it:
> **WhatsApp → Settings → Linked Devices → Link a Device**
>
> Auth is saved to `baileys/auth/` — you only do this once.
> If auth expires: `rm -rf baileys/auth/*` and restart.

### Auto-start at login

```bash
make install    # Registers macOS LaunchAgents — KIRA starts on every login
make uninstall  # Removes LaunchAgents
```

---

## Usage

Send any message starting with `/` to **yourself** in WhatsApp **Saved Messages**.

### Command examples

| Message | What happens |
|---------|-------------|
| `/hey what's up` | Casual chat reply |
| `/play lofi music on spotify` | Plays lofi on Spotify |
| `/search spotify synthwave` | Searches Spotify for synthwave |
| `/next track` | Skips to next Spotify track |
| `/volume high` | Sets volume to 85% |
| `/mute` | Mutes audio |
| `/open ~/Desktop/project in vscode` | Opens folder in VS Code |
| `/find all PDFs in ~/Documents` | Lists matching files |
| `/read ~/notes.txt` | Returns file contents |
| `/move ~/Desktop/file.txt to ~/Documents` | Moves a file |
| `/run ls -la ~/Desktop` | Runs terminal command, returns output |
| `/open https://github.com` | Opens URL in browser |
| `/search google best python libraries` | Googles it |
| `/what's on my calendar today` | Lists today's Calendar events |
| `/remind me to call John tomorrow` | Creates a Reminder |
| `/screenshot` | Takes a screenshot |
| `/copy hello world` | Writes to clipboard |
| `/what's in my clipboard` | Reads clipboard |
| `/notify Meeting in 5 minutes` | Sends macOS banner notification |
| `/open Slack` | Opens Slack |
| `/quit Slack` | Quits Slack |
| `/lock my mac` | Locks the screen |
| `/sleep` | Puts Mac to sleep |
| `/wifi off` | Turns Wi-Fi off |
| `/what's the date` | Returns current date and time |
| `/clean downloads and organize by type` | Multi-step plan with streaming status |

### Multi-step plans

For complex tasks KIRA builds a plan and streams each step back:

```
You:  /backup my Desktop to ~/Backups and notify me when done

KIRA: 🧠 Analyzing your goal...
      📋 3-step plan ready. Starting...
      ⏳ Step 1: Create ~/Backups if it doesn't exist
      ⏳ Step 2: Copy Desktop to ~/Backups/Desktop
      ⏳ Step 3: Notify — backup complete
      ✅ Plan complete.
```

Plans can pause mid-execution to ask you a question:

```
KIRA: ❓ Should I overwrite existing files in ~/Backups?
      Reply to continue.

You:  yes
KIRA: 🔄 Resuming plan...
```

### Risky action confirmation

Destructive operations always ask before running:

```
You:  /delete ~/Downloads/old-project

KIRA: ⚠️ Risky action detected:
      Tool: filesystem_op
      Reason: Filesystem delete operation
      Reply YES to run it or NO to cancel.
      (Auto-cancels in 2 minutes)

You:  yes
KIRA: ✅ Moved ~/Downloads/old-project to Trash
```

---

## Security

### Two-layer risk detection

**Layer 1 — Instant regex blocks (always enforced):**
- `rm -rf`, `sudo`, dangerous `chmod`
- `DROP TABLE`, `kill -9`, `mkfs`, `dd if=`
- Writes to `/dev/`
- Fork bombs `:(){...}`
- Command substitution `$(...)` and backtick execution
- Pipe chains `cmd | cmd`

**Layer 2 — Groq LLM scoring:**
- Commands that pass Layer 1 get scored `low / medium / high`
- `high` → confirmation required
- Groq failure → defaults to risky (fail-safe)

Filesystem `delete` always requires confirmation, independent of both layers.

---

## Memory

KIRA remembers past interactions using **Mem0** backed by **ChromaDB** (embedded local vector store) with **Ollama** (`nomic-embed-text`) for embeddings.

- Every exchange (message + reply) is stored after the conversation
- Relevant memories are retrieved and injected into the LLM context on each new message
- Scoped per user (`user_id = "me"`)
- Fully local — stored in `agent/chroma_db/`
- **Lazily initialized** — memory client connects to Ollama on first use, not at server startup

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Required. Get from [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model for chat, planning, and tool selection |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL for embeddings |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `CHROMA_PATH` | `./agent/chroma_db` | ChromaDB persistence directory |

Rate limit: **60 messages/minute** — change `RATE_LIMIT` in `agent/middleware/rate_limiter.py`.

---

## Logs

```bash
tail -f /tmp/wa-agent.log      # Python FastAPI agent
tail -f /tmp/wa-baileys.log    # Node Baileys client

make logs                      # Both at once
```

---

## Troubleshooting

**QR code not appearing / "Connection Failure"**
```bash
rm -rf baileys/auth/*
# Restart Baileys — a fresh QR will appear
```

**Agent hangs on startup**
- Ollama must be running before the agent starts: `ollama serve`
- Check Redis: `redis-cli ping` → should return `PONG`

**`code` command not found**
- VS Code → `Cmd+Shift+P` → `Shell Command: Install 'code' command in PATH`

**Spotify search not working**
- Ensure Spotify is open before sending search commands

**Volume command ignored**
- Accepted values: `0`–`100`, or `mute` / `low` / `medium` / `high`

**Rate limit hit**
- Default: 60 messages/minute. Increase `RATE_LIMIT` in `agent/middleware/rate_limiter.py`

---

## Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq API (Llama 3.3 70B) |
| WhatsApp | Baileys `@whiskeysockets/baileys` |
| Web framework | FastAPI + Uvicorn |
| Memory | Mem0 OSS + ChromaDB + Ollama |
| Session store | Redis |
| Mac automation | AppleScript + macOS CLI (`open`, `screencapture`, `pbcopy`, etc.) |
| Runtime | Python 3.11, Node.js 18 |

---

## License

MIT
