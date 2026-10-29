"""YAKO jury one-click entry using an existing demo identity."""
from app_qvac_financial.server.security.authentication.yako_csrf import yako_csrf_protect
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from app_qvac_financial.server.security.authentication import web
from app_qvac_financial.server.django.models.authentication import QVACWebCredential

@yako_csrf_protect
@require_POST
def jury_access(request):
    if os.environ.get('AI_YAKO_JURY_ACCESS_ENABLED') != '1':
        return JsonResponse({'error': 'Jury access is currently unavailable.'}, status=503)
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    if web.throttle('jury-access-ip|' + ip, failed=True):
        return JsonResponse({'error': 'Too many attempts. Please try again later.'}, status=429)
    identity = web.current_identity(request)
    if identity is None:
        credential = (QVACWebCredential.objects.select_related('identity')
            .filter(email='jury-demo@example.com', disabled_at__isnull=True,
                    identity__is_active=True, identity__suspended_at__isnull=True)
            .first())
        if credential is None:
            return JsonResponse({'error': 'Demo account has not been provisioned.'}, status=503)
        identity = credential.identity
    token = web.issue_session(identity)
    response = JsonResponse({'ok': True})
    response.set_cookie(web.COOKIE, token, **web.cookie_options(request))
    response['Cache-Control'] = 'no-store'
    return response
