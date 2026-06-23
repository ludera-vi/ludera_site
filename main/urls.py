"""
URL-маршруты приложения main.

'app_name' позволяет ссылаться на эти маршруты по именам в шаблонах.
Например: {% url 'main:index' %} вернёт '/' — главную страницу.
"""
from django.urls import path
from . import views

# app_name — пространство имён для маршрутов этого приложения
app_name = 'main'

# urlpatterns — список всех URL-шаблонов приложения
urlpatterns = [
    path('', views.index, name='index'),
    path('ecosystem-test/', views.ecosystem_test, name='ecosystem_test'),
    path('contact/', views.contact_submit, name='contact_submit'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
    path('blog/<uslug:slug>/', views.blog_detail, name='blog_detail'),
    path('projects/<uslug:slug>/', views.project_detail, name='project_detail'),
    path('services/<uslug:slug>/', views.service_detail, name='service_detail'),
    path('products/<uslug:slug>/', views.product_detail, name='product_detail'),
]
