"""Independent authentication endpoints; no LojasNova user/session access."""
from app_qvac_financial.server.security.authentication.yako_csrf import yako_csrf_page
from app_qvac_financial.server.security.authentication.yako_csrf import yako_csrf_protect
import json, uuid
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from app_qvac_financial.server.security.authentication import web, device as device_auth
from app_qvac_financial.server.django.models import QVACDevice
from app_qvac_financial.server.django.models.authentication import QVACWebSession, QVACDeviceSession
from app_qvac_financial.server.django.models.security import QVACAccessGrant

def payload(request):
    if len(request.body)>8192: raise ValueError('Request too large')
    value=json.loads(request.body.decode('utf-8'))
    if not isinstance(value,dict): raise ValueError('Object required')
    return value

def fail(message='Invalid request',status=400): return JsonResponse({'error':message},status=status)

@yako_csrf_page
@ensure_csrf_cookie
@require_GET
def sign_in_page(request):
    if web.current_identity(request): return redirect('app_qvac_financial:workspace')
    return render(request,'app_qvac_financial/sign_in.html')

@yako_csrf_page
@ensure_csrf_cookie
@require_GET
def sign_up_page(request):
    if web.current_identity(request): return redirect('app_qvac_financial:workspace')
    return render(request, 'app_qvac_financial/sign_up.html')

@yako_csrf_protect
@require_POST
def register(request):
    try:
        data=payload(request)
        # Count failed attempts as well as successful requests; never trust browser-provided IP headers.
        ip=request.META.get('REMOTE_ADDR','unknown')
        if web.throttle('register-ip|'+ip, failed=True):
            return fail('Too many registration attempts',429)
        identity=web.register(data['email'],data['password'])
        token=web.issue_session(identity)
    except PermissionError: return fail('Registration unavailable: capacity reached',403)
    except (KeyError,ValueError,TypeError): return fail('Registration unavailable or invalid',400)
    except Exception as exc:
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError
        if isinstance(exc,(ValidationError,IntegrityError)): return fail('Registration unavailable or invalid',403)
        raise
    response=JsonResponse({'ok':True});response.set_cookie(web.COOKIE,token,**web.cookie_options(request));response['Cache-Control']='no-store';return response

@yako_csrf_protect
@require_POST
def sign_in(request):
    try:
        data=payload(request)
        email=data['email'];password=data['password']
        if not isinstance(email,str) or not isinstance(password,str) or len(email)>254 or len(password)>256: return fail('Invalid credentials',401)
        ip=request.META.get('REMOTE_ADDR','unknown')
        identity=web.login(email,password,ip)
    except (KeyError,ValueError,TypeError): return fail('Invalid credentials',401)
    if identity is None: return fail('Invalid credentials',401)
    token=web.issue_session(identity)
    response=JsonResponse({'ok':True});response.set_cookie(web.COOKIE,token,**web.cookie_options(request));response['Cache-Control']='no-store';return response

@yako_csrf_protect
@require_POST
def sign_out(request):
    raw=request.COOKIES.get(web.COOKIE,'')
    if raw: QVACWebSession.objects.filter(token_digest=web.digest(raw)).update(revoked_at=timezone.now())
    response=JsonResponse({'ok':True});response.delete_cookie(web.COOKIE,path='/qvac-financial/',samesite='Strict');response['Cache-Control']='no-store';return response

@require_GET
def me(request):
    identity=web.current_identity(request)
    if not identity: return fail('Authentication required',401)
    response=JsonResponse({'identity_id':str(identity.public_id)});response['Cache-Control']='no-store';return response

@require_POST
def challenge(request):
    try:
        data=payload(request)
        from app_qvac_financial.server.security.authentication.web import throttle
        key='device-challenge|'+request.META.get('REMOTE_ADDR','unknown')
        if throttle(key,failed=True): return fail('Too many requests',429)
        dev=QVACDevice.objects.select_related('identity').get(public_id=uuid.UUID(data['device_id']))
        cid,nonce=device_auth.new_challenge(dev)
        response=JsonResponse({'challenge_id':str(cid),'nonce':nonce,'expires_in':90,'algorithm':'Ed25519'})
        response['Cache-Control']='no-store';return response
    except (KeyError,ValueError,TypeError,QVACDevice.DoesNotExist,PermissionError): return fail('Device unavailable',403)

@require_POST
def verify(request):
    try:
        data=payload(request)
        from app_qvac_financial.server.security.authentication.web import throttle
        key='device-verify|'+request.META.get('REMOTE_ADDR','unknown')
        if throttle(key,failed=True): return fail('Too many requests',429)
        token=device_auth.complete_challenge(uuid.UUID(data['challenge_id']),data['nonce'],data['signature'])
        response=JsonResponse({'token':token,'token_type':'Bearer','expires_in':1200})
        response['Cache-Control']='no-store';return response
    except Exception as exc:
        from app_qvac_financial.server.django.models.authentication import QVACAuthChallenge
        if isinstance(exc,(KeyError,ValueError,TypeError,PermissionError,QVACAuthChallenge.DoesNotExist)):
            return fail('Authentication failed',403)
        raise

@require_GET
def device_me(request):
    header=request.headers.get('Authorization','')
    token=header[7:] if header.startswith('Bearer ') else ''
    device=device_auth.authenticated_device(token)
    if not device: return fail('Authentication required',401)
    scopes=list(QVACAccessGrant.objects.filter(device=device,revoked_at__isnull=True).filter(
        Q(expires_at__isnull=True)|Q(expires_at__gt=timezone.now())
    ).values_list('scope',flat=True))
    response=JsonResponse({'device_id':str(device.public_id),'identity_id':str(device.identity.public_id),'scopes':scopes});response['Cache-Control']='no-store';return response
