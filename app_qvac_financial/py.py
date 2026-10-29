#!/usr/bin/env python3
"""AI Yako jury one-click installer. No DB migrations, env exports, or manual provisioning."""
from pathlib import Path
import hashlib, os, tempfile, sys
from datetime import datetime

TARGET = Path('/home/farcry/Documents/ai-yako/app_qvac_financial/server/api/auth/jury.py')
BACKUPS = Path('/home/farcry/Downloads')
if not TARGET.is_file():
    sys.exit(f'ABORT: missing {TARGET}')
original = TARGET.read_text(encoding='utf-8')
# Accept only the two known prior versions, or the idempotent result.
known = ('def jury_access(request):' in original and
         'web.issue_session(identity)' in original and
         ('jury-demo@example.com' in original or 'test.jury@aiyako.com' in original))
if not known:
    sys.exit('ABORT: unexpected jury.py; no changes made')

replacement = '''"""One-click public jury demo (testnet/simulated data only)."""
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
'''
compile(replacement, str(TARGET), 'exec')
if original == replacement:
    print('Already installed; no changes necessary.')
    sys.exit(0)
BACKUPS.mkdir(parents=True, exist_ok=True)
digest = hashlib.sha256(original.encode('utf-8')).hexdigest()
backup = BACKUPS / f'ai_yako_jury_{datetime.now():%Y%m%d_%H%M%S}_{digest[:12]}.py.bak'
backup.write_text(original, encoding='utf-8')
if TARGET.read_text(encoding='utf-8') != original:
    sys.exit('ABORT: target changed during install')
fd, tmp = tempfile.mkstemp(prefix='.jury-', suffix='.py', dir=TARGET.parent)
try:
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(replacement)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, TARGET.stat().st_mode)
    os.replace(tmp, TARGET)
finally:
    if os.path.exists(tmp):
        os.unlink(tmp)
print('INSTALLED:', TARGET)
print('BACKUP:', backup)
print('No export needed. First button click provisions demo identity in PostgreSQL.')
print('IMPORTANT: publicly accessible shared demo account; ensure all finance routes are testnet-only.')