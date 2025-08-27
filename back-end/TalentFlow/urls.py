from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("api/", include("TalentFlow.api.urls")),
    path("api/auth/", include("TalentFlow.accounts.urls")),
    path("hr/", include("hr.urls")),
    path("attendance/", include("attendance.urls")),
    path("reports/", include("reports.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    # Debug only apps
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path("silk/", include("silk.urls", namespace="silk")),
    ]
    
    # Static + media serving only in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
