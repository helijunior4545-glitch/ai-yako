"""Ed25519 proof-of-possession and single-use DB challenges."""
import base64, hashlib, secrets
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from app_qvac_financial.server.django.models import QVACDevice
from app_qvac_financial.server.django.models.authentication import QVACAuthChallenge, QVACDeviceSession

CONTEXT=b'AI-YAKO-DEVICE-AUTH-v1\n'
def b64decode(value):
    if not isinstance(value,str) or len(value)>256: raise ValueError('Invalid encoding')
    return base64.urlsafe_b64decode(value+'='*(-len(value)%4))
def b64encode(value): return base64.urlsafe_b64encode(value).decode().rstrip('=')
def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def new_challenge(device):
    if device.revoked_at or not device.verified_at or not device.identity.is_active or device.identity.suspended_at:
        raise PermissionError('Device unavailable')
    nonce=secrets.token_urlsafe(32)
    challenge=QVACAuthChallenge.objects.create(device=device,nonce_digest=digest(nonce),expires_at=timezone.now()+timedelta(seconds=90))
    return challenge.public_id, nonce

def complete_challenge(challenge_id, nonce, signature):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    with transaction.atomic():
        challenge=QVACAuthChallenge.objects.select_for_update().select_related('device__identity').get(public_id=challenge_id)
        device=challenge.device
        if challenge.consumed_at or challenge.expires_at<=timezone.now() or device.revoked_at or not device.verified_at or not device.identity.is_active or device.identity.suspended_at:
            raise PermissionError('Challenge unavailable')
        if not secrets.compare_digest(challenge.nonce_digest,digest(nonce)) or device.authentication_algorithm!='Ed25519':
            raise PermissionError('Challenge invalid')
        try:
            pub=b64decode(device.authentication_public_key)
            Ed25519PublicKey.from_public_bytes(pub).verify(b64decode(signature),CONTEXT+str(challenge.public_id).encode()+b'\n'+nonce.encode())
        except (ValueError, InvalidSignature) as exc:
            raise PermissionError('Signature invalid') from exc
        challenge.consumed_at=timezone.now(); challenge.save(update_fields=['consumed_at'])
        raw=secrets.token_urlsafe(48)
        QVACDeviceSession.objects.create(device=device,token_digest=digest(raw),expires_at=timezone.now()+timedelta(minutes=20))
        return raw

def authenticated_device(token):
    if not token or len(token)>256: return None
    row=QVACDeviceSession.objects.select_related('device__identity').filter(token_digest=digest(token),revoked_at__isnull=True,expires_at__gt=timezone.now(),device__revoked_at__isnull=True,device__verified_at__isnull=False,device__identity__is_active=True,device__identity__suspended_at__isnull=True).first()
    return row.device if row else None
