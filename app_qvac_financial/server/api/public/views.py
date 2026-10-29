"""Public product pages. No wallet/identity/private data exposed."""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def landing(request):
    from app_qvac_financial.landing import content as landing_content
    return landing_content.page(request)

@require_GET
def workspace(request):
    from app_qvac_financial.server.security.authentication.web import current_identity
    from django.shortcuts import redirect
    if not current_identity(request):
        return redirect('app_qvac_financial:sign_in_page')
    return render(request, 'app_qvac_financial/workspace.html')

@require_GET
def capabilities(request):
    response = JsonResponse({'product':'AI Yako', 'version':'3.0.0',
        'qvac_inference':False, 'wdk_signing':False, 'wallet_connected':False,
        'device_pairing':False, 'sync':False, 'demo_data':False,
        'mode':'interface_only', 'transactions_enabled':False})
    response['Cache-Control']='no-store'
    return response