# google_fit_project/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Include allauth URLs
    path('', include('fit_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
