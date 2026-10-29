"""One-click public jury demo (testnet/simulated data only)."""
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from app_qvac_financial.server.security.authentication.yako_csrf import yako_csrf_protect
from app_qvac_financial.server.security.authentication import web
from app_qvac_financial.server.django.models import QVACIdentity
from app_qvac_financial.server.django.models.authentication import QVACWebCredential

DEMO_EMAIL = 'test.jury@aiyako.com'


def get_demo_identity():
    # Serialize first-time creation across concurrent requests and workers.
    with transaction.atomic(using='default'):
        from django.db import connection
        if connection.vendor != 'postgresql':
            raise RuntimeError('AI Yako jury demo requires PostgreSQL')
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_advisory_xact_lock(%s)', [527219114])
        credential = (QVACWebCredential.objects.using('default')
                      .select_related('identity').filter(email=DEMO_EMAIL).first())
        if credential is None:
            identity = QVACIdentity.objects.using('default').create()
            QVACWebCredential.objects.using('default').create(
                identity=identity, email=DEMO_EMAIL,
                password_hash=make_password(None))  # No usable password.
            return identity
        if (credential.disabled_at is not None or
                not credential.identity.is_active or
                credential.identity.suspended_at is not None):
            return None  # Explicitly disabled accounts must stay disabled.
        return credential.identity


@yako_csrf_protect
@require_POST
def jury_access(request):
    # Always use the dedicated demo identity, never an arbitrary signed-in user.
    try:
        identity = get_demo_identity()
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Jury demo provisioning failed')
        return JsonResponse({'error': 'Demo temporarily unavailable.'}, status=503)
    if identity is None:
        return JsonResponse({'error': 'Demo account is disabled.'}, status=403)
    token = web.issue_session(identity)
    response = JsonResponse({'ok': True})
    response.set_cookie(web.COOKIE, token, **web.cookie_options(request))
    response['Cache-Control'] = 'no-store'
    return response
