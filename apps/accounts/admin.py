from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from .models import Role, AuditLog

User = get_user_model()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name",
                    "role", "is_active", "is_verified", "date_joined"]
    list_filter = ["is_active", "is_staff", "is_verified", "role"]
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name",
         "last_name", "phone_number", "avatar")}),
        ("Role & Access", {"fields": ("role", "is_active", "is_staff",
         "is_verified", "is_superuser", "must_change_password")}),
        ("Groups & Permissions", {"fields": ("groups", "user_permissions")}),
        ("Timestamps", {
         "fields": ("date_joined", "last_login", "last_login_ip")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2", "is_active"),
        }),
    )
    readonly_fields = ["date_joined", "last_login", "last_login_ip"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "ip_address", "timestamp"]
    list_filter = ["action"]
    search_fields = ["user__email", "description"]
    readonly_fields = ["user", "action",
                       "description", "ip_address", "timestamp"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
