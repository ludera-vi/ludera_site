from django.contrib import admin
from .models import Client, Call, Board, Column, Card, Chat, ChatMember, ChatMessage


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'company_name', 'city', 'assigned_manager', 'is_archived', 'created_at']
    list_filter = ['is_archived', 'legal_status', 'city']
    search_fields = ['name', 'phone', 'company_name', 'comment']


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ['client', 'manager', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['client__name', 'client__phone', 'comment']


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at']


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'position']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'column', 'client', 'responsible', 'created_at']
    list_filter = ['column__board']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['title', 'chat_type', 'client', 'card', 'created_at']
    list_filter = ['chat_type', 'is_deleted']


@admin.register(ChatMember)
class ChatMemberAdmin(admin.ModelAdmin):
    list_display = ['chat', 'user', 'is_active']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'author', 'created_at']
