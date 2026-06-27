from django.contrib import admin
from .models import Client, Call


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
