from django.urls import path
from . import views
from . import site_urls

app_name = 'sales'

urlpatterns = [
    path('login/', views.manager_login, name='login'),
    path('logout/', views.manager_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
] + site_urls.urlpatterns
