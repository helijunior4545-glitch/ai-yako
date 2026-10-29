"""AI Yako non-custodial product metadata. No prompts, seeds or signing keys."""
import uuid
from django.db import models
from django.db.models import Q


class QVACAgentProfile(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    identity = models.ForeignKey('app_qvac_financial.QVACIdentity', on_delete=models.CASCADE, related_name='agent_profiles')
    agent_kind = models.CharField(max_length=40)
    display_name = models.CharField(max_length=120)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model_artifact = models.ForeignKey('app_qvac_financial.QVACModelArtifact', null=True, blank=True, on_delete=models.SET_NULL, related_name='agent_profiles')
    configuration = models.JSONField(default=dict, blank=True, help_text='Non-sensitive settings only. Never store prompts, keys or private financial data.')
    policy_version = models.CharField(max_length=40, blank=True, default='')

    class Meta:
        app_label = 'app_qvac_financial'
        constraints = [models.UniqueConstraint(fields=['identity', 'agent_kind'], name='qvac_unique_agent_kind')]


class QVACModelArtifact(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    model_identifier = models.CharField(max_length=180)
    version = models.CharField(max_length=64)
    sha256 = models.CharField(max_length=64)
    byte_size = models.PositiveBigIntegerField()
    verified_at = models.DateTimeField(null=True, blank=True)
    format = models.CharField(max_length=40, blank=True, default='')
    runtime_name = models.CharField(max_length=80, blank=True, default='')
    signature_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'app_qvac_financial'
        constraints = [models.UniqueConstraint(fields=['model_identifier', 'version', 'sha256'], name='qvac_unique_model_artifact'), models.CheckConstraint(condition=Q(byte_size__gt=0), name='qvac_artifact_size_positive')]


class QVACWalletPublicReference(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device = models.ForeignKey('app_qvac_financial.QVACDevice', on_delete=models.PROTECT, related_name='wallet_references')
    chain = models.CharField(max_length=48)
    network = models.CharField(max_length=48, default='testnet')
    public_address = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    disabled_at = models.DateTimeField(null=True, blank=True)
    address_format = models.CharField(max_length=32, blank=True, default='')

    class Meta:
        app_label = 'app_qvac_financial'
        constraints = [models.UniqueConstraint(fields=['device', 'chain', 'network', 'public_address'], name='qvac_unique_wallet_public_ref')]
        indexes = [models.Index(fields=['device', 'network'], name='qvac_wallet_device_net_idx')]


class QVACAnalysisReceipt(models.Model):
    """Digest-only receipt; never store private prompts, raw analyses or secrets."""
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device = models.ForeignKey('app_qvac_financial.QVACDevice', on_delete=models.PROTECT)
    result_digest = models.CharField(max_length=64)
    agent_kind = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    model_artifact = models.ForeignKey('app_qvac_financial.QVACModelArtifact', null=True, blank=True, on_delete=models.SET_NULL)
    correlation_id = models.UUIDField(null=True, blank=True)
    inference_duration_ms = models.PositiveIntegerField(null=True, blank=True)
    outcome = models.CharField(max_length=24, default='completed', choices=[('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')])

    class Meta:
        app_label = 'app_qvac_financial'
        indexes = [models.Index(fields=['device', 'created_at'], name='qvac_receipt_device_idx')]


class QVACPairingRequest(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    identity = models.ForeignKey('app_qvac_financial.QVACIdentity', on_delete=models.CASCADE)
    requesting_device_public_key = models.TextField()
    challenge_digest = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    requesting_device_name = models.CharField(max_length=120, blank=True, default='')
    authentication_algorithm = models.CharField(max_length=32, blank=True, default='')
    attempt_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        app_label = 'app_qvac_financial'
        indexes = [models.Index(fields=['identity', 'expires_at'], name='qvac_pairing_expiry_idx')]
        constraints = [models.UniqueConstraint(fields=['challenge_digest'], name='qvac_pairing_challenge_uniq'), models.CheckConstraint(condition=Q(attempt_count__lte=10), name='qvac_pairing_attempt_limit')]
