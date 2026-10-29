"""Public landing content, staff-only editor, and atomic publication."""
import hashlib
import json
import os
import tempfile
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import user_passes_test
from django.utils.html import escape

CONTENT_PATH = Path(getattr(settings, "YAKO_LANDING_CONTENT_PATH", Path(settings.BASE_DIR) / "var" / "yako_landing_content.json"))
DEFAULT = {
    "hero_title": "Clarity is a new kind of power.",
    "hero_description": "Meet a more thoughtful way to understand your finances. Watch AI Yako in action.",
    "video_title": "See intelligence in motion.",
    "video_description": "A closer look at the thinking behind the interface.",
    "video_url": "", "poster_url": "", "captions_url": ""
}
FIELDS = set(DEFAULT)
PLATFORMS = {"Linux", "Windows", "Android", "macOS"}


def _load():
    try:
        data = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return dict(DEFAULT)
        result = {k: data.get(k, v) if isinstance(data.get(k, v), str) else v for k,v in DEFAULT.items()}
        result["releases"] = _releases(data.get("releases", []))
        return result
    except (OSError, ValueError):
        return {**DEFAULT, "releases": []}

def _valid_url(value):
    if not value: return True
    if value.startswith("/") and not value.startswith("//") and "\\" not in value: return True
    from urllib.parse import urlsplit
    p=urlsplit(value)
    return p.scheme == "https" and bool(p.netloc) and not p.username and not p.password

def _releases(value):
    if not isinstance(value, list): return []
    result=[]
    for row in value[:12]:
        if not isinstance(row, dict): continue
        item={key: str(row.get(key, "")).strip() for key in ("platform", "label", "version", "size", "url", "sha256")}
        if item["platform"] not in PLATFORMS or not item["url"].startswith("https://") or not _valid_url(item["url"]): continue
        if not item["version"] or not item["label"]: continue
        if len(item["label"])>90 or len(item["version"])>40 or len(item["size"])>30: continue
        if item["sha256"] and not __import__("re").fullmatch(r"[0-9a-fA-F]{64}",item["sha256"]): continue
        result.append(item)
    return result

@require_GET
def page(request):
    return render(request, "app_qvac_financial/landing.html", {"landing_content":_load()})

@require_GET
def public_content(request):
    data=_load()
    raw=json.dumps(data,sort_keys=True,ensure_ascii=False).encode("utf-8")
    tag='"'+hashlib.sha256(raw).hexdigest()+'"'
    if request.headers.get("If-None-Match")==tag:
        r=HttpResponse(status=304)
    else:
        r=JsonResponse({"version":tag.strip('"')[:12],"content":data})
    r["ETag"]=tag
    r["Cache-Control"]="public, max-age=30, must-revalidate"
    return r

def _staff(user):
    return user.is_authenticated and user.is_active and user.is_staff

@user_passes_test(_staff,login_url="/admin/login/")
@csrf_protect
def editor(request):
    data=_load()
    message=""
    if request.method=="POST":
        values={k:str(request.POST.get(k,"")).strip() for k in FIELDS}
        try:
            raw_releases=json.loads(request.POST.get("releases", "[]"))
            if not isinstance(raw_releases,list) or len(raw_releases)>12 or len(_releases(raw_releases))!=len(raw_releases): raise ValueError()
            values["releases"]=_releases(raw_releases)
        except (ValueError,TypeError):
            raw_releases=None
        if raw_releases is None:
            message="Invalid releases JSON. Use a list with platform, label, version, size, url (HTTPS), sha256 (optional)."
        elif any(len(v)> (3000 if k.endswith("description") else 400) for k,v in values.items() if isinstance(v,str)):
            message="Content exceeds the allowed length."
        elif not all(_valid_url(values[k]) for k in ("video_url","poster_url","captions_url")):
            message="Media URLs must be HTTPS or local paths beginning with /."
        else:
            CONTENT_PATH.parent.mkdir(parents=True,exist_ok=True)
            fd,tmp=tempfile.mkstemp(prefix=".yako-landing-",dir=str(CONTENT_PATH.parent))
            try:
                with os.fdopen(fd,"w",encoding="utf-8") as f:
                    json.dump(values,f,ensure_ascii=False,indent=2)
                    f.flush();os.fsync(f.fileno())
                os.chmod(tmp,0o600)
                os.replace(tmp,CONTENT_PATH)
                data=values
                message="Published successfully."
            finally:
                if os.path.exists(tmp):os.unlink(tmp)
    from django.middleware.csrf import get_token
    csrf=get_token(request)
    form=''.join('<label style="display:block;margin:20px 0">'+escape(k.replace("_"," ").title())+
        '<textarea name="'+escape(k)+'" rows="'+('3' if 'description' in k else '1')+
        '" style="display:block;width:100%;padding:12px;background:#111;color:#eee;border:1px solid #555">'+
        escape(data[k])+'</textarea></label>' for k in sorted(FIELDS))
    form += '<label style="display:block;margin:20px 0">Published downloads (JSON list)<textarea name="releases" rows="12" style="display:block;width:100%;padding:12px;background:#111;color:#eee;border:1px solid #555">'+escape(json.dumps(data.get("releases",[]),ensure_ascii=False,indent=2))+'</textarea></label>'
    html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Yako Landing Editor</title><body style="background:#080a0d;color:#eee;font:16px system-ui;max-width:780px;margin:45px auto;padding:20px"><h1>AI Yako · Landing Editor</h1><p>Staff only · Changes publish immediately · HTTPS media URLs</p><p>'+escape(message)+'</p><form method="post"><input type="hidden" name="csrfmiddlewaretoken" value="'+escape(csrf)+'">'+form+'<button style="padding:15px 25px">Publish changes</button></form></body></html>'
    r=HttpResponse(html)
    r["Cache-Control"]="no-store"
    r["X-Robots-Tag"]="noindex,nofollow"
    return r
