# AI Yako V9 — Linux QVAC GUI

Launch: `python3 yako_v9_desktop.py` from this directory.

Modes: deterministic rules; deterministic rules + official QVAC catalog model.

Requires `tkinter` and `tetherto-qvac-sdk` installed in the selected Python environment, plus the SDK worker.

QVAC model is loaded per analysis and unloaded afterward to reduce resident memory. The first use may contact the QVAC registry. Offline operation is **not yet certified**.

No wallet signing, no transfers, no Django session. Evidence contains scenario-derived information.

Tests: `python3 -m unittest test_yako_v9.py`.
