"""Wire-level contracts. No Django, wallet SDK or network dependency."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

PROTOCOL_VERSION = 1

@dataclass(frozen=True)
class SyncEnvelope:
    protocol_version: int
    event_id: UUID
    device_id: UUID
    event_type: str
    payload_digest: str
    created_at_utc: str

@dataclass(frozen=True)
class TransactionIntent:
    intent_id: UUID
    chain: str
    destination: str
    amount_base_units: str
    asset_identifier: str
    expires_at_utc: Optional[str] = None

@dataclass(frozen=True)
class ApprovalDecision:
    intent_id: UUID
    approved: bool
    approved_at_utc: str
    local_authorization_reference: str
