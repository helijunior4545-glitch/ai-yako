"""Only non-transactional metadata may enter automatic synchronization."""
class UnsafeSyncEvent(ValueError): pass
ALLOWED_KINDS = frozenset({"settings.changed", "analysis.saved", "device.metadata.updated"})

def validate_sync_kind(kind: str):
    if kind not in ALLOWED_KINDS: raise UnsafeSyncEvent("Event cannot be auto-synchronized")
