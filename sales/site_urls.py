from django.urls import path
from . import views
from main.cabinet_views import suggestion_mark_read

urlpatterns = [
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

    # Kanban
    path('kanban/', views.kanban_list, name='kanban_list'),
    path('kanban/<int:pk>/', views.kanban_board, name='kanban_board'),
    path('kanban/create-board/', views.kanban_create_board, name='kanban_create_board'),
    path('kanban/<int:pk>/delete-board/', views.kanban_delete_board, name='kanban_delete_board'),
    path('kanban/create-column/', views.kanban_create_column, name='kanban_create_column'),
    path('kanban/column/<int:pk>/edit/', views.kanban_edit_column, name='kanban_edit_column'),
    path('kanban/column/<int:pk>/delete/', views.kanban_delete_column, name='kanban_delete_column'),
    path('kanban/column/<int:pk>/toggle/', views.kanban_toggle_column, name='kanban_toggle_column'),
    path('kanban/create-card/', views.kanban_create_card, name='kanban_create_card'),
    path('kanban/card/<int:pk>/', views.kanban_card_detail, name='kanban_card_detail'),
    path('kanban/card/<int:pk>/delete/', views.kanban_delete_card, name='kanban_delete_card'),
    path('kanban/card/<int:pk>/move/', views.kanban_move_card, name='kanban_move_card'),
    path('kanban/reorder-columns/', views.kanban_reorder_columns, name='kanban_reorder_columns'),
    path('kanban/clients-json/', views.kanban_clients_json, name='kanban_clients_json'),

    # Chats
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/create/', views.chat_create, name='chat_create'),
    path('chats/<int:pk>/', views.chat_detail, name='chat_detail'),
    path('chats/<int:pk>/send/', views.chat_send, name='chat_send'),
    path('chats/<int:pk>/messages-json/', views.chat_messages_json, name='chat_messages_json'),
    path('chats/<int:pk>/add-member/', views.chat_add_member, name='chat_add_member'),
    path('chats/<int:pk>/remove-member/', views.chat_remove_member, name='chat_remove_member'),
    path('chats/<int:pk>/delete/', views.chat_delete, name='chat_delete'),
    path('chats/unread-count/', views.chat_unread_count, name='chat_unread_count'),

    # Info topics
    path('info/', views.info_list, name='info_list'),
    path('info/create/', views.info_create, name='info_create'),
    path('info/<int:pk>/', views.info_detail, name='info_detail'),
    path('info/<int:pk>/edit/', views.info_edit, name='info_edit'),
    path('info/<int:pk>/delete/', views.info_delete, name='info_delete'),
]
