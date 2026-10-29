"""Independent security metadata. No Django auth or commercial dependencies."""
import uuid
from django.db import models


class QVACAccessGrant(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device = models.ForeignKey('app_qvac_financial.QVACDevice', on_delete=models.CASCADE, related_name='access_grants')
    scope = models.CharField(max_length=80)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    grant_reason = models.CharField(max_length=120, blank=True, default='')
    policy_version = models.CharField(max_length=40, blank=True, default='')

    class Meta:
        app_label = 'app_qvac_financial'
        constraints = [models.UniqueConstraint(fields=['device', 'scope'], name='qvac_unique_device_scope')]
        indexes = [models.Index(fields=['device', 'revoked_at'], name='qvac_grant_device_rev_idx')]


class QVACSecurityEvent(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device = models.ForeignKey('app_qvac_financial.QVACDevice', null=True, on_delete=models.SET_NULL)
    event_type = models.CharField(max_length=96)
    occurred_at = models.DateTimeField(auto_now_add=True)
    details_digest = models.CharField(max_length=64, blank=True)
    correlation_id = models.UUIDField(null=True, blank=True)
    severity = models.CharField(max_length=16, default='info', choices=[('info', 'Info'), ('warning', 'Warning'), ('critical', 'Critical')])
    identity = models.ForeignKey('app_qvac_financial.QVACIdentity', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'app_qvac_financial'
        indexes = [models.Index(fields=['event_type', 'occurred_at'], name='qvac_security_type_idx'), models.Index(fields=['identity', 'occurred_at'], name='qvac_security_owner_idx')]
