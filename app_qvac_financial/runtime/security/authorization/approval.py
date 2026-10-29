"""Approval proof contract. This does NOT establish authentic human approval."""
from dataclasses import dataclass
from datetime import datetime, timezone

class ApprovalUnavailable(PermissionError): pass

@dataclass(frozen=True)
class ApprovalProof:
    intent_digest: str
    device_id: str
    approved_at_utc: str
    challenge_signature: bytes

class LocalApprovalVerifier:
    """Fail closed until platform keystore, trusted UI and signature verifier exist."""
    def verify(self, intent, proof: ApprovalProof) -> None:
        raise ApprovalUnavailable("Hardware-backed approval verification not integrated")
