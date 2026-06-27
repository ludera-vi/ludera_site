from django.contrib import admin
from .models import UserProfile, UserProduct, ProductFile, UserSetting, ManagerSuggestion, SuggestionMessage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'role', 'email_verified', 'phone_verified', 'created_at']
    list_filter = ['email_verified', 'phone_verified']
    search_fields = ['user__email', 'user__username', 'phone']


@admin.register(UserProduct)
class UserProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'is_active', 'purchased_at', 'expires_at']
    list_filter = ['is_active', 'product']
    search_fields = ['user__email', 'product__title']


@admin.register(ProductFile)
class ProductFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'file_type', 'order']


@admin.register(UserSetting)
class UserSettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(ManagerSuggestion)
class ManagerSuggestionAdmin(admin.ModelAdmin):
    list_display = ['manager', 'short_message', 'status', 'is_closed', 'created_at']
    list_filter = ['status', 'is_closed']
    search_fields = ['manager__email', 'message']
    readonly_fields = ['created_at', 'updated_at']

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Сообщение'


@admin.register(SuggestionMessage)
class SuggestionMessageAdmin(admin.ModelAdmin):
    list_display = ['suggestion', 'author', 'short_message', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['message', 'author__email']

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Сообщение'
