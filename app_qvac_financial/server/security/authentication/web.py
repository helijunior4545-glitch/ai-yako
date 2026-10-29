"""Independent web authentication. Never use commercial Django login."""
import hashlib, hmac, os, secrets
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from app_qvac_financial.server.django.models import QVACIdentity
from app_qvac_financial.server.django.models.authentication import QVACWebCredential, QVACWebSession, QVACLoginThrottle

COOKIE = 'qvac_web_session'

def digest(value): return hashlib.sha256(value.encode('utf-8')).hexdigest()

def cookie_options(request):
    return dict(httponly=True, secure=True, samesite='Strict', path='/qvac-financial/', max_age=8*3600)

def issue_session(identity):
    raw = secrets.token_urlsafe(48)
    QVACWebSession.objects.create(identity=identity, token_digest=digest(raw), expires_at=timezone.now()+timedelta(hours=8))
    return raw

def current_identity(request):
    raw = request.COOKIES.get(COOKIE, '')
    if not raw or len(raw)>256: return None
    session = QVACWebSession.objects.select_related('identity').filter(token_digest=digest(raw), revoked_at__isnull=True, expires_at__gt=timezone.now(), identity__is_active=True, identity__suspended_at__isnull=True).first()
    if not session: return None
    if not QVACWebCredential.objects.filter(identity=session.identity, disabled_at__isnull=True).exists(): return None
    return session.identity

def throttle(key, *, failed):
    """Database-backed conservative limit: 5 failures per 15 minutes per email+IP."""
    from django.db import IntegrityError
    now=timezone.now(); hashed=digest(key)
    try:
        with transaction.atomic():
            row, _ = QVACLoginThrottle.objects.select_for_update().get_or_create(key_digest=hashed, defaults={'window_started_at':now})
            if row.window_started_at < now-timedelta(minutes=15):
                row.window_started_at=now; row.failures=0
            blocked=row.failures>=5
            if failed: row.failures=min(65535,row.failures+1)
            row.save(update_fields=['window_started_at','failures'])
            return blocked
    except IntegrityError:
        return True

def validate_password(password):
    if not isinstance(password,str) or len(password)<14 or len(password)>256:
        raise ValueError('Password must have 14-256 characters')
    from django.contrib.auth.password_validation import validate_password as django_validate
    django_validate(password)

def registration_limit():
    """Configured per deployment. 0 disables new registrations; existing users can log in."""
    raw = os.environ.get('AI_YAKO_MAX_USERS', '20')
    try:
        value = int(raw)
    except (ValueError, TypeError):
        raise RuntimeError('AI_YAKO_MAX_USERS must be a nonnegative integer')
    if not 0 <= value <= 1000000:
        raise RuntimeError('AI_YAKO_MAX_USERS outside supported range')
    return value


def register(email, password):
    """Public, capped registration. Uses PostgreSQL transaction advisory lock to avoid oversubscription."""
    if not isinstance(email, str) or len(email) > 254:
        raise ValueError('Invalid email')
    email = email.strip().lower()
    validate_email(email)
    validate_password(password)
    from django.db import connections
    from django.db.models import Count
    from django.core.exceptions import ValidationError as DjangoValidationError
    from django.db import IntegrityError as DjangoIntegrityError

    # Serialize all registrations across Django workers/containers sharing the default PostgreSQL DB.
    with transaction.atomic(using='default'):
        connection = connections['default']
        if connection.vendor != 'postgresql':
            raise RuntimeError('Registration cap requires PostgreSQL')
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_advisory_xact_lock(%s)', [527219113])
        limit = registration_limit()
        if limit == 0 or QVACWebCredential.objects.using('default').count() >= limit:
            raise PermissionError('Registration limit reached')
        if QVACWebCredential.objects.using('default').filter(email=email).exists():
            raise ValueError('Registration unavailable')
        identity = QVACIdentity.objects.using('default').create()
        QVACWebCredential.objects.using('default').create(
            identity=identity, email=email, password_hash=make_password(password)
        )
    return identity

def login(email,password,ip):
    email=email.strip().lower(); key=f'{email}|{ip}'
    if throttle('login-ip|'+ip,failed=False): return None
    if throttle('login-account|'+email,failed=False): return None
    if throttle(key,failed=False): return None
    credential=QVACWebCredential.objects.select_related('identity').filter(email=email).first()
    # Dummy hash prevents easy timing differentiation of unknown accounts.
    hashed=credential.password_hash if credential else make_password('dummy-never-valid')
    valid=check_password(password,hashed)
    if not valid or not credential or credential.disabled_at or not credential.identity.is_active or credential.identity.suspended_at:
        throttle(key,failed=True); throttle('login-ip|'+ip,failed=True); throttle('login-account|'+email,failed=True); return None
    return credential.identity
