from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views as main_views

handler404 = main_views.handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cabinet/', include('main.cabinet_urls')),
    path('manager/', include('sales.urls')),
    path('account/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('main.urls')),
]

if settings.DEBUG and settings.MEDIA_URL and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG and settings.STATIC_URL:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
