"""
URL configuration for cybercell project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from crime_report.error_handlers import handle_404, handle_500, handle_403, handle_400

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crime_report.urls')),
]

if settings.DEBUG:
    # Serve static files from development server
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serve media files from development server
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Also serve files from STATICFILES_DIRS
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)

# Error handlers
handler404 = 'crime_report.error_handlers.handle_404'
handler500 = 'crime_report.error_handlers.handle_500'
handler403 = 'crime_report.error_handlers.handle_403'
handler400 = 'crime_report.error_handlers.handle_400'