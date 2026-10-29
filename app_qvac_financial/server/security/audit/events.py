"""Structured audit event, no secrets in metadata."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class AuditEvent:
    action: str
    identity_id: str
    device_id: str
    occurred_at_utc: str

def new_event(action, identity_id, device_id):
    return AuditEvent(action, identity_id, device_id, datetime.now(timezone.utc).isoformat())
