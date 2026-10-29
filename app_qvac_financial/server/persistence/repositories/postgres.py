"""PostgreSQL-backed Django ORM metadata repository.

Uses host DATABASE_ROUTERS; never assumes a tenant DB alias. No wallet secrets.
"""
from django.db import transaction
from ...django.models import QVACIdentity, QVACDevice
from ...django.models.product import QVACAgentProfile


class IdentityRepository:
    @staticmethod
    def get_by_public_id(public_id):
        return QVACIdentity.objects.get(public_id=public_id)

    @staticmethod
    def list_devices(identity):
        return QVACDevice.objects.filter(identity=identity, revoked_at__isnull=True).order_by('-registered_at')

    @staticmethod
    def list_agents(identity):
        return QVACAgentProfile.objects.filter(identity=identity).order_by('agent_kind')

    @staticmethod
    def register_device(identity, *, display_name):
        if not display_name or len(display_name) > 120:
            raise ValueError('Valid display_name required')
        # This is an internal repository method, NOT a public pairing endpoint.
        # Device registration must be guarded by authenticated service-layer policy.
        with transaction.atomic():
            return QVACDevice.objects.create(identity=identity, display_name=display_name)
