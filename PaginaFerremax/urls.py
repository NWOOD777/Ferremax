"""
URL configuration for PaginaFerremax project.

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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('appFerremax.urls')),         
    path('api/', include('appFerremax.api_urls')),  
]

# Serve static and media files in both development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# Configure custom error handlers

def handler404(request, exception):
    return render(request, 'home/404.html', status=404)

def handler500(request):
    return render(request, 'home/500.html', status=500)

def handler403(request, exception):
    return render(request, 'home/403.html', status=403)

def handler400(request, exception):
    return render(request, 'home/400.html', status=400)
