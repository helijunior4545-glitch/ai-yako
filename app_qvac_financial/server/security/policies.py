"""Server-side authorization primitives independent of commercial accounts."""
from dataclasses import dataclass

class AccessDenied(PermissionError):
    pass

@dataclass(frozen=True)
class Principal:
    identity_id: str
    device_id: str
    active: bool = True


def authorize_device(principal: Principal, owner_identity_id: str) -> None:
    if not principal.active or not principal.device_id or principal.identity_id != owner_identity_id:
        raise AccessDenied("Device not authorized for identity")
