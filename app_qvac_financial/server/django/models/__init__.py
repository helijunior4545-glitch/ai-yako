"""Independent AI Yako identity and device metadata. No signing secrets."""
import uuid
from django.db import models
from django.db.models import Q


class QVACIdentity(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "app_qvac_financial"


class QVACDevice(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    identity = models.ForeignKey(QVACIdentity, on_delete=models.CASCADE, related_name="devices")
    display_name = models.CharField(max_length=120)
    registered_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    authentication_public_key = models.TextField(blank=True, default="")
    authentication_algorithm = models.CharField(max_length=32, blank=True, default="")
    verified_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    platform = models.CharField(max_length=32, blank=True, default="")

    class Meta:
        app_label = "app_qvac_financial"
        indexes = [models.Index(fields=["identity", "revoked_at"], name="qvac_device_identity_rev_idx")]
        constraints = [
            models.CheckConstraint(condition=Q(verified_at__isnull=True) | ~Q(authentication_public_key=""), name="qvac_verified_has_pubkey"),
        ]


class QVACSyncEvent(models.Model):
    event_id = models.UUIDField(unique=True)
    device = models.ForeignKey(QVACDevice, on_delete=models.PROTECT)
    event_type = models.CharField(max_length=96)
    payload_digest = models.CharField(max_length=64)
    received_at = models.DateTimeField(auto_now_add=True)
    correlation_id = models.UUIDField(null=True, blank=True)
    processing_status = models.CharField(max_length=24, default="received", choices=[("received", "Received"), ("processed", "Processed"), ("rejected", "Rejected")])

    class Meta:
        app_label = "app_qvac_financial"
        indexes = [models.Index(fields=["device", "received_at"]), models.Index(fields=["processing_status", "received_at"], name="qvac_sync_status_time_idx")]

from .yako_chat_v1036 import YakoWebConversation, YakoWebMessage  # V10.36
