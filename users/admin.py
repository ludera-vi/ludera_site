from django.contrib import admin
from .models import UserProfile, UserProduct, ProductFile, UserSetting


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
