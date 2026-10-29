from app_qvac_financial.server.api.auth.jury import jury_access  # YAKO_JURY_V1055
"""AI Yako public jury landing + independent private auth. No financial endpoints."""
from django.urls import path
from .server.api.health.views import liveness
from .server.api.public.views import landing, workspace, capabilities
from .server.api.auth import views as auth
from .server.api.public.demo import jury_demo
app_name = 'app_qvac_financial'
urlpatterns = [
    path('auth/jury-access/', jury_access, name='jury_access'),  # YAKO_JURY_V1055
    path('', landing, name='landing'),
    path('app/', workspace, name='workspace'),
    path('health/', liveness, name='health'),
    path('capabilities/', capabilities, name='capabilities'),
    path('auth/', auth.sign_in_page, name='sign_in_page'),
    path('auth/signup/', auth.sign_up_page, name='sign_up_page'),
    path('demo/', jury_demo, name='jury_demo'),
    path('auth/register/', auth.register, name='register'),
    path('auth/login/', auth.sign_in, name='sign_in'),
    path('auth/logout/', auth.sign_out, name='sign_out'),
    path('auth/me/', auth.me, name='me'),
    path('auth/device/challenge/', auth.challenge, name='device_challenge'),
    path('auth/device/verify/', auth.verify, name='device_verify'),
    path('auth/device/me/', auth.device_me, name='device_me'),
]

from django.views.decorators.csrf import ensure_csrf_cookie
urlpatterns = [p if p.name != 'workspace' else path('app/', ensure_csrf_cookie(workspace), name='workspace') for p in urlpatterns]
# AI Yako V10.36 — authenticated financial intelligence endpoints
from .server.api.public import yako_runtime_v1036 as yako36
urlpatterns += [
    path('api/analyze', yako36.analyze_stream, name='yako36_analyze'),
    path('api/simulate', yako36.simulate, name='yako36_simulate'),
    path('api/conversations', yako36.conversations, name='yako36_conversations'),
    path('api/messages', yako36.messages, name='yako36_messages'),
    path('api/model-capabilities', yako36.model_capabilities, name='yako36_model_capabilities'),
    path('api/offline-status', yako36.offline_status, name='yako36_offline_status'),
]
# AI Yako V10.51 — public landing content and staff editor
from .landing import content as yako_landing_content
urlpatterns += [
    path('landing/content/', yako_landing_content.public_content, name='landing_content'),
    path('landing/editor/', yako_landing_content.editor, name='landing_editor'),
]
