"""Device operations disabled until cryptographic auth and DB grants exist."""
from django.http import JsonResponse

def device_endpoint(request):
    return JsonResponse({"error":"device_auth_not_configured"},status=503)
