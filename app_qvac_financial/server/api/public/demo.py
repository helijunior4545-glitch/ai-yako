"""Read-only public juror demonstration: no identity, wallet, or database reads."""
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache

@never_cache
@require_GET
def jury_demo(request):
    response = render(request, 'app_qvac_financial/jury_demo.html')
    response['Content-Security-Policy'] = "default-src 'none'; style-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response
