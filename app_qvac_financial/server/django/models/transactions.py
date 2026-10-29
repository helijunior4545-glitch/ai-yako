"""Financial intent metadata only. A database status is never signing authorization."""
import uuid
from django.db import models
from django.db.models import Q


class QVACTransactionIntent(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('prepared', 'Prepared'), ('awaiting_approval', 'Awaiting approval'),
        ('approved', 'Approved'), ('signed', 'Signed'), ('broadcast', 'Broadcast'),
        ('confirmed', 'Confirmed'), ('rejected', 'Rejected'), ('expired', 'Expired'), ('failed', 'Failed'),
    ]
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device = models.ForeignKey('app_qvac_financial.QVACDevice', on_delete=models.PROTECT)
    chain = models.CharField(max_length=48)
    network = models.CharField(max_length=48, default='testnet')
    intent_digest = models.CharField(max_length=64)
    status = models.CharField(max_length=24, default='draft', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    broadcast_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    transaction_hash = models.CharField(max_length=160, blank=True, default='')
    idempotency_key = models.UUIDField(null=True, blank=True)
    asset_identifier = models.CharField(max_length=80, blank=True, default='')
    # Amount/destination stay on the signing device. intent_digest commits to exact details.
    approval_proof_digest = models.CharField(max_length=64, blank=True, default='')
    failure_code = models.CharField(max_length=80, blank=True, default='')

    class Meta:
        app_label = 'app_qvac_financial'
        constraints = [
            models.UniqueConstraint(fields=['device', 'idempotency_key'], condition=Q(idempotency_key__isnull=False), name='qvac_unique_device_idempotency'),
            models.CheckConstraint(condition=Q(network='testnet'), name='qvac_intent_testnet_only'),
        ]
        indexes = [models.Index(fields=['device', 'status', 'created_at'], name='qvac_intent_device_state_idx')]
