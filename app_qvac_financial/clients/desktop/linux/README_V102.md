# AI Yako V10.2 — Conversational Financial Intelligence

New local-first conversational workstation with an original responsive dark UI, animated microinteractions, evidence panel, deterministic financial simulator, local SQLite conversations, and official QVAC SDK streamed inference.

## Run

```bash
python3 app_qvac_financial/clients/desktop/linux/yako_v102_server.py
```

Opens a local browser at `http://127.0.0.1:<random-port>/`. Uses Python stdlib HTTP server, CSS and JavaScript; **not React/TypeScript yet**. No npm install or external assets. Browser must support fetch streaming.

## Important

- No Django deployment required. Requires existing QVAC SDK, Bare worker and cached Llama 3.2 1B model.
- API bound to 127.0.0.1 with per-process random header token, Origin checks, and no external network endpoint. The SDK itself may consult registries: offline behavior must be tested with networking disconnected.
- Chat history is stored **unencrypted** in `~/.local/share/ai-yako-v102/history.sqlite3` (directory 0700, file 0600). Do not enter confidential information. Delete this file to erase local chat history after closing the app.
- No wallet signing, financial transfers, or live market data.
- Rules are limited patterns, not fraud detection proof. Model-generated text may contain unsupported claims; findings remain separately traceable to exact scenario text.
- QVAC responses are not fact-checked automatically. The app labels them as model output and falls back to deterministic findings on errors/refusal.
- One model load per request; on low-memory systems, avoid multiple concurrent QVAC requests (the UI limits one request per tab, not across tabs).
- HTTP service is for trusted single-user local machines, not exposed on a LAN or deployed publicly.
