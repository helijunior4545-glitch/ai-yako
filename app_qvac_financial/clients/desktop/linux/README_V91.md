# AI Yako V9.1 — Linux

Run: `python3 yako_v91_desktop.py` from this directory using the environment with `tetherto-qvac-sdk` and Tkinter.

V9.1 adds measured worker/model/generation times, shorter evidence-first Portuguese prompts, and recognition of variable monthly rates (10%+). It does NOT change V6–V9 or install SDK/model dependencies.

The model is still loaded/unloaded per request to limit resident RAM on 4GB systems. The prompt requests a short response but the SDK is not configured with a hard token limit. Text is model-generated and may contain unsupported claims. The `network_isolation_verified` report field remains false because the application itself cannot prove network isolation.

Tests: `python3 -m unittest test_yako_v91.py`.
