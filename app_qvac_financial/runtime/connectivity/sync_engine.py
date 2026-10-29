"""Sync is deliberately disabled until identity, auth and idempotency are built."""
class SyncNotConfigured(RuntimeError):
    pass

def synchronize(*args, **kwargs):
    raise SyncNotConfigured("Authenticated synchronization not implemented in V1")
