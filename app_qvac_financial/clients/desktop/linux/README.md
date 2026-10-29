# AI Yako Linux desktop — challenge preview

This is a local-first Tkinter desktop application, not a Django wrapper. It provides deterministic risk flags and an optional *generic* local GGUF command-line inference adapter. The generic adapter is NOT proof of QVAC SDK integration; use only a legitimately obtained, compatible model/runner and verify provenance and offline behavior. The installer does not download models, connect to remote endpoints or execute transactions. WDK and wallet signing are intentionally disabled.

Run `python3 yako_desktop.py`; test `python3 -m unittest test_yako_desktop.py`. Requires a Linux desktop with Python 3 and tkinter (`python3-tk` on many Debian-based distributions). For optional local inference, provide an executable compatible with llama.cpp CLI flags and a local GGUF file. No model is bundled. Use offline testing with networking disabled.

The generated `.desktop` launcher lives in `~/.local/share/applications/ai-yako.desktop`. It uses the absolute local path and is installed only with `--apply`. Use `--rollback` to restore backed-up files and remove this launcher's changes. The source installer is intended to be saved as `py.py` locally.
