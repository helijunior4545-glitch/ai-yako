# AI Yako challenge desktop V6

Status: Linux desktop prototype with offline deterministic checks and an optional local GGUF CLI runner. QVAC SDK integration: pending verification. WDK integration: pending. Wallet custody and financial signing: disabled. No real money or testnet broadcasts. Desktop app does not depend on the Django host or its database. The host app and migrations remain unchanged.

Acceptance gates: launch desktop; pass unittest; disconnect networking; verify deterministic mode; obtain official QVAC model/runtime and validate compatibility and model signature; verify inference offline; implement human approval; integrate WDK testnet only after independent safety review; record reproducible evidence. No mock output may be labeled as QVAC inference.
