"""Independent web credentials, sessions and single-use challenges. No host AUTH_USER_MODEL."""
import uuid
from django.db import models

class QVACWebCredential(models.Model):
    identity = models.OneToOneField('app_qvac_financial.QVACIdentity', on_delete=models.CASCADE, related_name='web_credential')
    email = models.EmailField(unique=True, max_length=254)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    disabled_at = models.DateTimeField(null=True, blank=True)
    class Meta: app_label = 'app_qvac_financial'

class QVACWebSession(models.Model):
    identity = models.ForeignKey('app_qvac_financial.QVACIdentity', on_delete=models.CASCADE)
    token_digest = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = 'app_qvac_financial'
        indexes = [models.Index(fields=['identity', 'expires_at'], name='qvac_web_session_idx')]

class QVACAuthChallenge(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device = models.ForeignKey('app_qvac_financial.QVACDevice', on_delete=models.CASCADE)
    nonce_digest = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: app_label = 'app_qvac_financial'

class QVACDeviceSession(models.Model):
    device = models.ForeignKey('app_qvac_financial.QVACDevice', on_delete=models.CASCADE)
    token_digest = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: app_label = 'app_qvac_financial'

class QVACLoginThrottle(models.Model):
    key_digest = models.CharField(max_length=64, unique=True)
    window_started_at = models.DateTimeField()
    failures = models.PositiveSmallIntegerField(default=0)
    class Meta: app_label = 'app_qvac_financial'
