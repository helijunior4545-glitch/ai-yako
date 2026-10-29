"""Scoped CSRF for YAKO; no dependency on LojasNova CSRF cookie.

The Django global CSRF check is skipped ONLY for views using this decorator.
Each such view validates a signed, expiring double-submit token and origin.
"""
import hmac
from functools import wraps
from urllib.parse import urlsplit
from django.conf import settings
from django.core import signing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

COOKIE = 'yako_csrf_token'
SALT = 'app_qvac_financial.yako_csrf.v1059'
MAX_AGE = 8 * 3600
PREFIX = '/qvac-financial/'

def _secure(request):
    # Always Secure on production HTTPS; localhost HTTP supported only in DEBUG.
    return not (settings.DEBUG and request.get_host().split(':')[0] in ('localhost', '127.0.0.1'))

def _options(request):
    return dict(path=PREFIX, secure=_secure(request), httponly=False,
                samesite='Strict', max_age=MAX_AGE)

def _issue(response, request):
    import secrets
    token = signing.dumps({'nonce': secrets.token_urlsafe(32)}, salt=SALT)
    response.set_cookie(COOKIE, token, **_options(request))
    response['Cache-Control'] = 'no-store'
    return response

def _origin_ok(request):
    # Compare against the externally visible origin (Django trusted proxy settings).
    expected = urlsplit(request.build_absolute_uri('/'))
    for key in ('HTTP_ORIGIN', 'HTTP_REFERER'):
        value = request.META.get(key)
        if value:
            try:
                got = urlsplit(value)
                if got.scheme != expected.scheme or got.netloc != expected.netloc:
                    return False
            except ValueError:
                return False
    # Browser requests must supply Origin or Referer; do not allow neither.
    return bool(request.META.get('HTTP_ORIGIN') or request.META.get('HTTP_REFERER'))

def yako_csrf_page(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        if request.method == 'GET' and response.status_code == 200:
            return _issue(response, request)
        return response
    return wrapped

def yako_csrf_protect(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            cookie = request.COOKIES.get(COOKIE, '')
            header = request.headers.get('X-YAKO-CSRF', '')
            if not cookie or not header or not hmac.compare_digest(cookie, header):
                return JsonResponse({'error': 'YAKO CSRF token missing or invalid'}, status=403)
            try:
                data = signing.loads(cookie, salt=SALT, max_age=MAX_AGE)
                if not isinstance(data, dict) or not data.get('nonce'):
                    raise signing.BadSignature('Invalid payload')
            except signing.BadSignature:
                return JsonResponse({'error': 'YAKO CSRF token expired or invalid'}, status=403)
            if not _origin_ok(request):
                return JsonResponse({'error': 'YAKO request origin rejected'}, status=403)
        return view(request, *args, **kwargs)
    return csrf_exempt(wrapped)
