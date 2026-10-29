"""Device challenge records. Signature verification remains mandatory and unimplemented."""
import secrets
from datetime import datetime, timedelta, timezone

class DeviceChallenge:
    def __init__(self, device_id, ttl_seconds=90):
        self.device_id=device_id
        self.nonce=secrets.token_urlsafe(32)
        self.expires_at=datetime.now(timezone.utc)+timedelta(seconds=ttl_seconds)
        self.consumed=False

    def consume(self):
        if self.consumed or datetime.now(timezone.utc)>=self.expires_at:
            raise PermissionError("Challenge expired or already used")
        self.consumed=True

class ChallengeVerifierUnavailable(RuntimeError): pass

def verify_device_signature(*args, **kwargs):
    raise ChallengeVerifierUnavailable("Trusted device public-key verification not integrated")
