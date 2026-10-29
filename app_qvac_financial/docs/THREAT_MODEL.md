# AI Yako threat model — V2

## Assets
Local wallet private keys, transaction approval, device credentials, encrypted financial records, model binaries, sync event integrity.

## Threats
Prompt injection; agent tool misuse; wallet exfiltration; approval replay; malicious or compromised sync server; model supply-chain substitution; unauthorized paired device; cross-app database privilege escalation; unsafe auto-update.

## Required mitigations before release
Platform keystore, local trusted UI approval tied to exact transaction digest, verified WDK transaction parameters, least-privilege DB role, challenge-response authentication, device revocation, replay cache, signed artifacts, encrypted local records, no remote access to signing keys.

## Trust boundaries
Server never owns wallet keys. QVAC output is untrusted. Sync events cannot authorize on-chain execution. Commercial Django authentication never grants AI Yako financial permissions.
