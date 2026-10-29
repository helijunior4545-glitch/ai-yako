"""Deterministic policy: never allow an agent to self-approve a transfer."""
class AuthorizationRequired(PermissionError):
    pass

def require_explicit_local_approval(*, approved: bool, actor: str) -> None:
    if not approved or actor != "human_local_user":
        raise AuthorizationRequired("Explicit local user authorization required")
