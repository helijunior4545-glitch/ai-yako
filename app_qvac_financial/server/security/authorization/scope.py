"""Scoped server grants, independent of Django user and commercial accounts."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AccessGrant:
    identity_id: str
    device_id: str
    scopes: frozenset[str]
    revoked: bool = False

def require_scope(grant: AccessGrant, *, identity_id: str, device_id: str, scope: str):
    if grant.revoked or grant.identity_id!=identity_id or grant.device_id!=device_id or scope not in grant.scopes:
        raise PermissionError("Missing device scope")
