# AI Yako V10.1 — Financial Intelligence Workstation

Refined Linux Tkinter UI with responsive side navigation, hover states, prominent analysis stages, immediate deterministic evidence, streaming QVAC tokens, scenario chart, local history and diagnostics.

## Start

```bash
python3 app_qvac_financial/clients/desktop/linux/yako_v101_desktop.py
```

Requires the V10 core (`yako_v10_core.py`) and QVAC bridge (`yako_v10_qvac.py`) already installed, Python with tkinter, and the official QVAC SDK and cached model for local inference. Does not download or install any packages or models. No Django deploy is required.

## Safety and limitations

- V10 and all earlier versions remain untouched. This is a new entry point.
- No wallet transactions, signing or transfers.
- The AI may be inaccurate, hallucinate or refuse legitimate requests. Deterministic findings are shown separately from AI text.
- The interface shows a local-first design, **not** a network-isolation proof. A cached model and network-disconnected test are required to establish offline behavior.
- History is stored in the existing unencrypted V10 SQLite database; avoid entering confidential financial information.
- UI effects use Tkinter hover and state transitions. No external frontend framework is installed.
- Actual graphical behavior and QVAC performance require validation on the target Linux desktop.
