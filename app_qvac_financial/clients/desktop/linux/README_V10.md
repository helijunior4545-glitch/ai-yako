# AI Yako V10 — Linux Financial Intelligence Workstation

A desktop workstation built with Python/Tkinter and the official QVAC SDK, preserving V6–V9.1.

## Modules
Overview, AI Intelligence (QVAC + rules), Risk Analysis, Scenario Lab (compound returns with local Canvas chart), History (local SQLite), Model Center.

## Run
`python3 app_qvac_financial/clients/desktop/linux/yako_v10_desktop.py`

Requires Tkinter and `tetherto-qvac-sdk` already installed in the Python environment, and a QVAC worker/model prepared in advance. The installer does **not** download packages or models. Initial model acquisition may require network access. Offline inference must be independently tested after model caching. A financial analysis is not advice or proof of fraud. No signing, wallet access or transfers.

## Validation
`cd app_qvac_financial/clients/desktop/linux && python3 -m unittest test_yako_v10.py`

## Limitations
The visual design is a first integrated desktop release, not yet a fully polished production UI. Model inference can take over a minute on low-memory hardware. QVAC output may be incorrect or refuse valid requests. No hard generation-token limit is configured. Closing the window during inference does not guarantee worker cancellation. SQLite local history is not encrypted; do not enter secrets. No claim of AGI or of tested Android/Windows compatibility.
