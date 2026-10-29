"""Do not mistake generated AI text for authoritative chain data."""
class UnverifiedChainState(RuntimeError): pass

def require_fresh_chain_state(*, verified: bool, timestamp_utc: str | None):
    if not verified or not timestamp_utc: raise UnverifiedChainState("Verified fresh chain state required")
