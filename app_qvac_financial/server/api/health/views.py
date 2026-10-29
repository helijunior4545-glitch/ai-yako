"""Minimal public liveness endpoint, no DB or secret details."""
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def liveness(request):
    return JsonResponse({"service":"ai-yako","status":"alive","api_version":2})
