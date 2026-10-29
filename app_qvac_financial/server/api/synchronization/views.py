"""Sync disabled until replay protection, encryption and auth are implemented."""
from django.http import JsonResponse

def sync_endpoint(request):
    return JsonResponse({"error":"sync_not_configured"},status=503)
