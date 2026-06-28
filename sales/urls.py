from django.urls import path
from . import views
from main.cabinet_views import suggestion_mark_read

app_name = 'sales'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/import/', views.client_import, name='client_import'),
    path('clients/export/', views.client_export, name='client_export'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/<int:pk>/create-call/', views.create_call, name='create_call'),
    path('clients/<int:pk>/edit/', views.client_update, name='client_update'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    path('clients/<int:pk>/archive/', views.toggle_archive, name='toggle_archive'),
    path('clients/<int:client_pk>/documents/<int:doc_pk>/delete/', views.delete_document, name='delete_document'),
    path('clients/deleted/', views.deleted_list, name='deleted_list'),
    path('clients/<int:pk>/restore/', views.client_restore, name='client_restore'),
    path('calls/<int:pk>/update/', views.call_update, name='call_update'),
    path('called/', views.called_list, name='called_list'),
    path('in-progress/', views.in_progress_list, name='in_progress_list'),
    path('archive/', views.archive_list, name='archive_list'),
    path('completed/', views.completed_list, name='completed_list'),
    path('refusal/', views.refusal_list, name='refusal_list'),
    path('clients/<int:pk>/restore-from-refusal/', views.client_restore_from_refusal, name='client_restore_from_refusal'),
    path('suggestions/', views.suggestion_list, name='suggestion_list'),
    path('suggestions/mark-read/', suggestion_mark_read, name='suggestion_mark_read'),
]
