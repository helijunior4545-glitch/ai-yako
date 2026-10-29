from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path(
        '',
        RedirectView.as_view(
            pattern_name='app_qvac_financial:landing',
            permanent=False,
        ),
        name='home',
    ),
    path('admin/', admin.site.urls),
    path('qvac-financial/', include('app_qvac_financial.urls')),
]