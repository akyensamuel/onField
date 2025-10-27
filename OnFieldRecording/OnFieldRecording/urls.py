"""
URL configuration for OnFieldRecording project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize admin site headers
admin.site.site_header = "OnField Recording Administration"
admin.site.site_title = "OnField Admin"
admin.site.index_title = "Welcome to OnField Recording System"


# Sentry Debug View (REMOVE IN PRODUCTION!)
def trigger_sentry_error(request):
    """
    Deliberately triggers an error to test Sentry integration.
    This endpoint should be REMOVED before production deployment!
    """
    division_by_zero = 1 / 0
    return division_by_zero  # This line will never execute


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('DataForm.urls')),  # Include DataForm app URLs
    path('sentry-debug/', trigger_sentry_error, name='sentry_debug'),  # TODO: REMOVE BEFORE PRODUCTION
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
